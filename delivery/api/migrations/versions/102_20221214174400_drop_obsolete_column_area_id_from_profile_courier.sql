-- upgrade --
ALTER TABLE "profile_courier" DROP COLUMN IF EXISTS "area_id";
ALTER TABLE "profile_courier" DROP CONSTRAINT IF EXISTS "fk_profile__area_8e3fd655";
-- downgrade --
ALTER TABLE "profile_courier" ADD COLUMN "area_id" INT REFERENCES "area" ("id") ON DELETE SET NULL;