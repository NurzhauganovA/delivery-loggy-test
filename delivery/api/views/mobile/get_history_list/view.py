import typing
from collections import defaultdict

from fastapi_pagination.ext.tortoise import paginate

from api import models, enums, schemas
from api.schemas import pagination
from api.schemas.mobile.get_history import GetHistoryResponse, HistoryImage


# TODO: нужен рефакторинг, тут N+1 проблема
async def __serialize_initiator_info(queryset):
    for history in queryset:
        if history.initiator_type in [
            enums.InitiatorType.USER.value, enums.InitiatorType.IMPORT.value
        ]:
            try:
                initiator = await models.user_get(with_history=False,
                                                  id=history.initiator_id)
                profiles = await models.get_all_user_profiles(initiator['id'])
                profile_types = ([history.initiator_role, ] if history.initiator_role
                                 else [value['type'] for value in profiles])
                history.initiator = {
                    'id': initiator['id'],
                    'profile_types': profile_types,
                    'first_name': initiator['first_name'],
                    'last_name': initiator['last_name'],
                    'middle_name': initiator['middle_name'],
                }
            except models.UserNotFound:
                history.initiator = {}
        else:
            initiator = await models.partner_get(
                partner_id=history.initiator_id, with_info=False
            )
            history.initiator = {
                'id': initiator.get('id', None),
                'name_en': initiator.get('name_en', None),
                'name_kk': initiator.get('name_kk', None),
                'name_ru': initiator.get('name_ru', None),
                'name_zh': initiator.get('name_zh', None),
            }

async def __add_images_to_comments(history_records: typing.List[GetHistoryResponse]) -> None:
    """
        Добавление значения в поле images к записям истории связанными с созданием комментария.
        При условии, что action_type = create_comment и в action_data есть поле id.

        Args:
            history_records: массив схем записей истории

        Returns:
            None
    """
    # Получаем записи из истории с action_type = create_comment и с id в action_data
    comment_history_records = []
    for history_record in history_records:
        if history_record.action_type == enums.ActionType.CREATE_COMMENT:
            if action_data := history_record.action_data:
               if action_data.get('id'):
                   comment_history_records.append(history_record)


    # Получаем список id комментариев
    comment_ids = []
    for comment_history_record in comment_history_records:
        comment_ids.append(comment_history_record.action_data['id'])

    # Получаем изображения по конкретным комментариям
    images = await models.CommentImage.filter(comment_id__in=comment_ids)

    # Группируем изображения по comment_id и переводим их в схему HistoryImage
    grouped_images = defaultdict(list)
    for image in images:
        history_image = HistoryImage(
            id=image.id,
            image=image.image,
        )
        grouped_images[image.comment_id].append(history_image)

    # Добавляем изображения к комментариям с action_type = create_comment
    for comment_history_record in comment_history_records:
        comment_id = comment_history_record.action_data['id']
        comment_history_record.images = grouped_images.get(comment_id)



async def get_history_list(
        pagination_params: pagination.Params,
        filter_params: typing.Optional[schemas.HistoryFilterParams],
) -> pagination.Page[GetHistoryResponse]:
    """
        Получение списка записей из истории с учетом пагинации, фильтрации и сортировки по убыванию

        Args:
            pagination_params: схема пагинации
            filter_params: схема фильтров

        Returns:
            Возвращает объект страницы Page с записями типа GetHistoryResponse
    """
    if not pagination_params:
        raise ValueError('pagination_params is required')

    params = filter_params.dict(exclude_unset=True, exclude_none=True) if filter_params else {}
    qs = models.History.filter(**params).order_by('-created_at')

    result = await paginate(qs, params=pagination_params)
    await __serialize_initiator_info(result.items)
    await __add_images_to_comments(result.items)

    return result
