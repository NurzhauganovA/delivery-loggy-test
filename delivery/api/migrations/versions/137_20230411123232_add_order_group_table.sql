-- upgrade --
CREATE TABLE IF NOT EXISTS "order_group" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "courier_id" INT REFERENCES "profile_courier" ("id") ON DELETE SET NULL,
    "courier_service_manager_id" INT REFERENCES "profile_service_manager" ("id") ON DELETE SET NULL,
    "delivery_point_id" INT REFERENCES "partner_shipment_point" ("id") ON DELETE SET NULL,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE,
    "shipment_point_id" INT REFERENCES "partner_shipment_point" ("id") ON DELETE SET NULL,
    "sorter_id" INT REFERENCES "profile_sorter" ("id") ON DELETE SET NULL
);
-- downgrade --
DROP TABLE IF EXISTS "order_group";
