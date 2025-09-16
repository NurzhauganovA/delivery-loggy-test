-- upgrade --
DELETE FROM
    "order.postcontrols" a
        USING "order.postcontrols" b
WHERE
    a.id < b.id
    AND a.order_id = b.order_id and a.config_id = b.config_id;
CREATE UNIQUE INDEX "uniq_order_postcontrol_on_order_and_config" ON "order.postcontrols" ("order_id", "config_id");
-- downgrade --
DROP INDEX "uniq_order_postcontrol_on_order_and_config";
