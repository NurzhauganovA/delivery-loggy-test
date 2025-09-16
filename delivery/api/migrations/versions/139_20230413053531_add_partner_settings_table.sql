-- upgrade --
DROP TABLE IF EXISTS "partner_setting";
CREATE TABLE IF NOT EXISTS "partner_setting" (
    "days_to_delivery" INT,
    "auto_item_for_order_group_id" INT REFERENCES "item" ("id") ON DELETE RESTRICT,
    "default_delivery_point_for_order_group_id" INT REFERENCES "partner_shipment_point" ("id") ON DELETE RESTRICT,
    "partner_id" INT NOT NULL  PRIMARY KEY REFERENCES "partner" ("id") ON DELETE CASCADE
);
INSERT INTO partner_setting (partner_id)
(SELECT id as partner_id FROM public."partner");
-- downgrade --
DROP TABLE IF EXISTS "partner_setting";
