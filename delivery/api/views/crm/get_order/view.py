from tortoise.expressions import Subquery, RawSQL
from tortoise.query_utils import Prefetch

from api import models, enums
from api.enums import PostControlType
from api.schemas.crm import GetOrderResponse
from api.schemas.order import SubStatusGet
from api.views.crm.get_order.cdek_status_mapping import get_cdek_status_name


async def get_order(
        order_id: int,
        default_filter_args: list = None,
) -> GetOrderResponse:
    if default_filter_args is None:
        default_filter_args = []
    has_ready_for_shipment = f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{enums.StatusSlug.READY_FOR_SHIPMENT}\")'"
    deliverygraph_step_count = 'jsonb_array_length("order__deliverygraph"."graph")'
    current_status_position = """(jsonb_path_query_first("order__deliverygraph"."graph", '$ ? (@.id == $val)', ('{
                      "val": ' || "order"."current_status_id" || '}')::jsonb)) ->> 'position'"""

    instance_qs = models.Order.all_objects.annotate(
        last_otp=Subquery(
            models.SMSPostControl.filter(
                order_id=RawSQL('"order"."id"'),
            ).order_by('-created_at').limit(1).values('created_at'),
        ),
        has_ready_for_shipment=RawSQL(has_ready_for_shipment),
        deliverygraph_step_count=RawSQL(deliverygraph_step_count),
        current_status_position=RawSQL(current_status_position),
    ).filter(
        *default_filter_args,
        deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
    ).distinct().get(id=order_id)
    statuses_args = []

    qs = instance_qs.prefetch_related(
        Prefetch(
            'courier_service_statuses',
            queryset=models.CourierServiceStatus.all().order_by('created_at'),
            to_attr='cdek_statuses'
        ),
        Prefetch('status_set', models.OrderStatuses.filter(*statuses_args).prefetch_related('status'),
                 'statuses'),
        Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
            parent_config_id__isnull=True,
            type=PostControlType.POST_CONTROL.value,
        ).prefetch_related(
            Prefetch('inner_param_set', models.PostControlConfig.filter(
                type=PostControlType.POST_CONTROL.value
            ).prefetch_related(
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'inner_params'),
            Prefetch(
                'postcontrol_document_set',
                models.PostControl.filter(order_id=order_id),
                'postcontrol_documents',
            ),
        ), 'postcontrol_configs'),
        Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
            parent_config_id__isnull=True,
            type=PostControlType.CANCELED.value,
        ).prefetch_related(
            Prefetch('inner_param_set', models.PostControlConfig.filter(
                type=PostControlType.CANCELED.value,
            ).prefetch_related(
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'inner_params'),
            Prefetch(
                'postcontrol_document_set',
                models.PostControl.filter(order_id=order_id),
                'postcontrol_documents',
            ),
        ), 'postcontrol_cancellation_configs'),

        # Запрашиваем комментарии с изображениями и ролью пользователя
        Prefetch(
            "comments",
            queryset=models.Comment.all().order_by('-created_at').select_related(
                'user_role'
            ).prefetch_related(
                'images'
            )
        )

    ).select_related(
        'area', 'city', 'courier__user', 'item', 'deliverygraph',
        'partner', 'current_status', 'shipment_point', 'delivery_point', 'product'
    )

    order_obj = await qs

    # Проставляем значение в поле courier_assigned_at
    order_obj.courier_assigned_at = None
    for status in order_obj.statuses:
        if status.status_id == 2:
            order_obj.courier_assigned_at = status.created_at
            break


    response = GetOrderResponse.from_orm(order_obj)

    cdek_sub_statuses_list = [
        SubStatusGet(
            name=get_cdek_status_name(css.status),
            created_at=css.created_at,
        )
        for css in getattr(order_obj, 'cdek_statuses', [])
    ]

    for status in response.statuses:
        if status.status.slug == enums.StatusSlug.TRANSFER_TO_CDEK:
            status.sub_statuses = cdek_sub_statuses_list
        elif not status.sub_statuses:
            del status.sub_statuses

    return response
