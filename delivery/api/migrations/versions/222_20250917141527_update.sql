-- upgrade --
CREATE TABLE IF NOT EXISTS "courier_service" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "courier_service" VARCHAR(256),
    "warehouse_id" VARCHAR(256),
    "city_id" INT NOT NULL REFERENCES "city" ("id") ON DELETE CASCADE,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE
);;
ALTER TABLE "item" ADD "item_identification_code" VARCHAR(256);
-- downgrade --
ALTER TABLE "item" DROP COLUMN "item_identification_code";
DROP TABLE IF EXISTS "courier_service";
