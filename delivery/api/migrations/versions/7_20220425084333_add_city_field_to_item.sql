-- upgrade --
ALTER TABLE "item" ADD "city_id" INT NULL;
ALTER TABLE "item" ADD CONSTRAINT "fk_item_city_a338db2b" FOREIGN KEY ("city_id") REFERENCES "city" ("id") ON DELETE RESTRICT;
-- downgrade --
ALTER TABLE "item" DROP CONSTRAINT "fk_item_city_a338db2b";
ALTER TABLE "item" DROP COLUMN "city_id";
