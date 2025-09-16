-- upgrade --
CREATE TABLE IF NOT EXISTS "item_shipment_points" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "item_id" INT NOT NULL REFERENCES "item" ("id") ON DELETE CASCADE,
    "shipment_point_id" INT NOT NULL REFERENCES "partner.addresses" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "item_shipment_points";
