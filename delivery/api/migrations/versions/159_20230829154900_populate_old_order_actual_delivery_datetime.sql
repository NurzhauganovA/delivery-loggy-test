-- upgrade --
update "order" set actual_delivery_datetime= subquery.created_at
from (SELECT DISTINCT ON (current_status.order_id)
current_status.order_id,
current_status.created_at
FROM "order.statuses" current_status
LEFT JOIN status text_status ON current_status.status_id = text_status.id
WHERE text_status.id IN (12, 7)
GROUP BY current_status.order_id, current_status.created_at
ORDER BY current_status.order_id, current_status.created_at) subquery where "order".id=subquery.order_id;
-- downgrade --
select '1';