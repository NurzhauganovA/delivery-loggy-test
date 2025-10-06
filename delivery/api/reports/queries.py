import datetime

from api.context_vars import locale_context

order_report_query = """
    WITH
        history_resolved AS (
            SELECT h.action_data, u.first_name as initiator_first_name, u.last_name as initiator_last_name, h.model_id, h.created_at, h.model_type from history h
            left join "user" u on u.id = initiator_id
            where model_type ='Order'
            and (h.action_data -> 'delivery_status' -> 'reason' is not null
            or h.action_data -> 'delivery_status' -> 'comment' is not null
            or h.action_data -> 'post-control' is not null
            or h.action_data -> 'delivery_status' ->> 'status' is not null)
            order by created_at DESC
        ),
        history_text AS (SELECT string_agg(
                                         concat(
                                                 case
                                                     when action_data -> 'delivery_status' is not null
                                                         then
                                                         case action_data -> 'delivery_status' ->> 'status'
                                                             when 'cancelled' then 'Отменена'
                                                             when 'postponed' then concat('Отложена',
                                                                                          concat(chr(10), ' Комментарий: ',
                                                                                                 action_data ->
                                                                                                 'delivery_status' ->>
                                                                                                 'comment',
                                                                                                 chr(10)))
                                                             when 'noncall' then 'Недозвон'
                                                             when 'on-the-way-to-call-point' then 'На пути к точке вывоза'
                                                             when 'is_delivered' then 'Доставлено'
                                                             when 'restored' then 'Восстановлена'
                                                             when 'rescheduled' then 'Перенос встречи'
                                                         end
                                                     when action_data -> 'post-control' is not null
                                                         then
                                                         case action_data ->> 'post-control'
                                                             when 'created' then 'Постконтроль создан'
                                                             when 'accepted' then 'Постконтроль утвержден'
                                                             when 'declined' then 'Постконтроль отклонен'
                                                         end
                                                     end, '(', initiator_first_name, ' ', initiator_last_name, ')',
                                                 ' >> Дата действия: (', created_at, ')'), '; ' order by created_at DESC) as text_history,
                                 history_resolved.model_id                                       as history_model_id,
                                 string_agg(
                                         case
                                             when history_resolved.action_data -> 'delivery_status' ->>
                                                  'comment' is not null
                                                 then concat(history_resolved.action_data ->
                                                             'delivery_status' ->> 'comment', ' >> ',
                                                             history_resolved.created_at, ', ')
                                             when history_resolved.action_data -> 'delivery_status' ->>
                                                  'reason' is not null
                                                 then concat(history_resolved.action_data ->
                                                             'delivery_status' ->> 'reason', ' >> ',
                                                             history_resolved.created_at, ', ')
                                             end
                                     , ' ' order by created_at DESC)       as delivery_status_comment
                          from history_resolved
                          where action_data is not null
                          group by model_id),
    postcontrol_creators_name as (
        select distinct on (model_id) case
       when u.first_name is not null and u.last_name is not null
           then concat(u.first_name, ' ', u.last_name,
                       ' (', u.phone_number, ')')
       end  as creator_name,
                       model_id as order_id
       from history hst
                left join "public".user u on u.id = hst.initiator_id
       where action_data -> 'post-control' is not null and initiator_role = 'courier'
         and action_data ->> 'post-control' = 'created'
    ),
    approvers_name as (
        select distinct on (model_id) model_id, case
        when u.first_name is not null and u.last_name is not null
           then concat(u.first_name, ' ', u.last_name,
                       ' (', u.phone_number, ')')
        end as approver_name, model_id as order_id, hst.created_at
        from history hst
                left join "public".user u on u.id = hst.initiator_id
        where action_data -> 'post-control' is not null
         and action_data ->> 'post-control' = 'accepted'
         order by hst.model_id, hst.created_at DESC
    ),
    last_status as (
		select distinct on (os.order_id) os.order_id, s.name_%(locale)s, os.created_at from public."order.statuses" os
        left join public."status" s on os.status_id = s.id
        order by os.order_id, os.created_at DESC
    ),
    courier_appointed_at as (
        select distinct on (os.order_id) os.order_id, os.created_at
        from public."order.statuses" os
        where os.status_id = 2
        order by os.order_id, os.created_at DESC
    )
    SELECT DISTINCT ord.id::text                                          as id,
                ord.partner_order_id                                      as partner_order_id,
                ord.created_at                                            as created_at,
                ord.receiver_name                                         as receiver_name,
                ord.receiver_iin                                          as receiver_iin,
                ord.receiver_phone_number                                 as receiver_phone_number,
                pr.attributes->>'pan'                                     as pan,
                case ord.type
                    when 'urgent' then 'срочная'
                    when 'planned' then 'плановая'
                    when 'pickup' then 'самовывоз'
                    end                                                   as type,
                ord.delivery_datetime                                     as delivery_datetime,
                ord.initial_delivery_datetime                             as initial_delivery_datetime,
                ord.actual_delivery_datetime                              as actual_delivery_datetime,
                ord.idn                                                   as idn,
                ord.manager                                               as manager,
                ord.courier_service                                       as courier_service,
                ord.track_number                                          as track_number,
                c.name_%(locale)s                                         as city,
                co.name_%(locale)s                                        as country,
                coalesce(p.name_%(locale)s, p.name_en, p.name_ru) as partner,
                i.name                                                    as "item",
                a.slug                                                    as area,
                CONCAT(us.first_name, ' ', us.last_name)                  as courier,
                CASE
                    WHEN ord.delivery_status::text <> '{}'::text THEN
                        CASE ord.delivery_status ->> 'status'
                            WHEN 'cancelled' THEN 'Отменена'
                            WHEN 'postponed' THEN 'Отложена'
                            WHEN 'cancelled_at_client' THEN 'Отказ с выездом'
                            WHEN 'rescheduled' THEN 'Перенос встречи'
                            WHEN 'noncall' THEN 'Недозвон'
                            WHEN 'is_delivered' THEN 'Доставлено'
                        ELSE ls.name_%(locale)s
                        END
                    ELSE
                        ls.name_%(locale)s
                    END
                                                                          as status,
                dad.address                                               as delivery_point,
                history_text.text_history                                 as history,
                history_text.delivery_status_comment                      as status_comment,
                pcr.creator_name                                          as postcontrol_creator_name,
                pap.approver_name                                         as postcontrol_approver_name,
                ls.name_%(locale)s 					                      as current_status_name,
				ls.created_at 							                  as current_status_datetime,
                caa.created_at                                            as courier_appointed_at
FROM "order" as ord
         left join city c on ord.city_id = c.id
         left join country co on co.id = c.country_id
         left join partner p on ord.partner_id = p.id
         left join item i on i.id = ord.item_id
         left join area a on ord.area_id = a.id
         left join profile_courier pc on ord.courier_id = pc.id
         left join "user" us on us.id = pc.user_id
         left join postcontrol_creators_name pcr on ord.id = pcr.order_id
         left join approvers_name pap on ord.id = pap.order_id
         left join "delivery_point" dad on ord.delivery_point_id = dad.id
         left join status s on ord.current_status_id = s.id
         left join history_text on ord.id=history_text.history_model_id
         left join last_status ls on ls.order_id=ord.id
         left join courier_appointed_at caa on caa.order_id=ord.id
         left join product pr on ord.id = pr.order_id
         %(filter_params)s
ORDER BY ord."created_at" DESC;
"""


def get_time_with_timezone(time, timezone_offset):
    if timezone_offset:
        if timezone_offset.total_seconds() >= 0:
            return time + datetime.timedelta(seconds=timezone_offset.total_seconds())
        else:
            return time - datetime.timedelta(seconds=timezone_offset.total_seconds() - timezone_offset.total_seconds() * 2)
    else:
        return time


def get_utc_zero_time(time, timezone_offset):
    result_time = time
    if timezone_offset:
        if timezone_offset.total_seconds() >= 0:
            result_time = time - datetime.timedelta(seconds=timezone_offset.total_seconds())
        else:
            result_time = time + datetime.timedelta(seconds=timezone_offset.total_seconds() - timezone_offset.total_seconds() * 2)
    return result_time


def order_report_query_builder(**kwargs):
    locale = locale_context.get()
    cities = kwargs.get('city_id__in', None)
    couriers = kwargs.get('courier_id__in', None)
    statuses = kwargs.get('current_status__in', None)
    shipment_points = kwargs.get('shipment_point_id__in', None)
    created_at_range = kwargs.get('created_at__range', None)
    partners = kwargs.get('partner_id__in', None)
    sorter_id = kwargs.pop('sorter_id', None)
    is_superuser = kwargs.pop('is_superuser', False)
    fact_delivery_time = kwargs.get('fact_delivery_time__range', None)
    were_in_status = kwargs.get('were_in_status', None)
    current_status_range = kwargs.get('current_status__created_at__range', None)
    idn_isnull = kwargs.get('idn__isnull')
    country_id = kwargs.get('city__country_id', None)
    courier_service = kwargs.get('courier_service')

    filtering_parameters = ''
    if sorter_id:
        filtering_parameters = 'left join order_group on ord.order_group_id=order_group.id \n'
    if is_superuser:
        filtering_parameters += f'WHERE true \n'
    if partners and not is_superuser:
        filtering_parameters += f'WHERE ord."partner_id" in ({", ".join([str(i) for i in partners])}) \n'
    if 'WHERE' not in filtering_parameters:
        filtering_parameters += 'WHERE true \n'
    if sorter_id:
        filtering_parameters += f'AND order_group.sorter_id = {sorter_id} \n'
    if created_at_range:
        utc_offset = created_at_range[0].utcoffset()
        filtering_parameters += f"""AND ord."created_at" BETWEEN '{get_utc_zero_time(created_at_range[0].replace(
            tzinfo=None
        ), utc_offset)}' and '{get_utc_zero_time(created_at_range[1].replace(tzinfo=None), utc_offset)}' \n"""
    if cities:
        filtering_parameters += f'AND c."id" in ({", ".join([str(i) for i in cities])}) \n'
    if couriers:
        filtering_parameters += f'AND ord."courier_id" in ({", ".join([str(i) for i in couriers])}) \n'
    if statuses:
        filtering_parameters += f'AND ord.current_status_id in ({", ".join([str(i) for i in statuses])}) \n'
    if shipment_points:
        filtering_parameters += f'AND ord.shipment_point_id IN  ({", ".join([str(i) for i in shipment_points])}) \n'
    if fact_delivery_time:
        utc_offset = fact_delivery_time[0].utcoffset()
        filtering_parameters += f"""AND ord.actual_delivery_datetime BETWEEN '{get_utc_zero_time(fact_delivery_time[0].replace(
            tzinfo=None
        ),utc_offset)}' and '{get_utc_zero_time(fact_delivery_time[1].replace(tzinfo=None), utc_offset)}' \n"""
    if current_status_range:
        utc_offset = current_status_range[0].utcoffset()
        filtering_parameters += f"""AND ls.created_at BETWEEN '{get_utc_zero_time(current_status_range[0].replace(
            tzinfo=None
        ), utc_offset)}' and '{get_utc_zero_time(current_status_range[1].replace(tzinfo=None), utc_offset)}' \n"""
    if were_in_status:
        filtering_parameters += f"""AND (select id from "order.statuses" where order_id = ord.id and status_id IN ({", ".join([str(i) for i in were_in_status])}) \nlimit 1) is not null"""
    if idn_isnull is not None:
        filtering_parameters += f'AND ord.idn IS {"" if idn_isnull else "NOT"} NULL \n'
    if country_id:
        filtering_parameters += f'AND co.id = {country_id} \n'
    if courier_service:
        filtering_parameters += f"AND ord.courier_service = '{courier_service}' \n"
    result = order_report_query % {'locale': locale, 'filter_params': filtering_parameters}
    return result
