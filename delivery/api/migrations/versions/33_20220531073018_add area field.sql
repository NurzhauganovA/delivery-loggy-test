-- upgrade --
ALTER TABLE "order" ADD "area_id" INT;
ALTER TABLE "profile_courier" ADD "area_id" INT;
ALTER TABLE "order" ADD CONSTRAINT "fk_order_area_3d8a8896" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE CASCADE;
ALTER TABLE "profile_courier" ADD CONSTRAINT "fk_profile__area_7e2fd544" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "profile_courier" DROP CONSTRAINT "fk_profile__area_7e2fd544";
ALTER TABLE "order" DROP CONSTRAINT "fk_order_area_3d8a8896";
ALTER TABLE "order" DROP COLUMN "area_id";
ALTER TABLE "profile_courier" DROP COLUMN "area_id";
