-- upgrade --
DELETE
FROM "order.statuses"
WHERE id IN
      (SELECT id
       FROM (SELECT id,
                    ROW_NUMBER() OVER ( PARTITION BY order_id, status_id
                        ORDER BY id ) AS row_num
             FROM "order.statuses") t
       WHERE t.row_num > 1);
CREATE UNIQUE INDEX "uid_order.statu_order_i_5c99c5" ON "order.statuses" ("order_id", "status_id");
-- downgrade --
DROP INDEX "uid_order.statu_order_i_5c99c5";
