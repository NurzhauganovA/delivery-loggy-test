-- upgrade --
ALTER TABLE "profile_courier" DROP CONSTRAINT "fk_profile__area_8e3fd655";
ALTER TABLE "profile_courier" DROP COLUMN "area_id";
CREATE TABLE "profile_courier_area" ("area_id" INT NOT NULL REFERENCES "area" ("id") ON DELETE CASCADE,"profile_courier_id" INT NOT NULL REFERENCES "profile_courier" ("id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "profile_courier_area";
ALTER TABLE "profile_courier" ADD "area_id" INT;
ALTER TABLE "profile_courier" ADD CONSTRAINT "fk_profile__area_8e3fd655" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE RESTRICT;
