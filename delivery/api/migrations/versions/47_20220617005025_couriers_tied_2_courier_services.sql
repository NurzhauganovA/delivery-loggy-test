-- upgrade --
ALTER TABLE "profile_courier" ADD "partner_id" INT NOT NULL DEFAULT 1;
ALTER TABLE "profile_courier" ADD CONSTRAINT "fk_profile__partner_7a6cd292" FOREIGN KEY ("partner_id") REFERENCES "partner" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "profile_courier" DROP CONSTRAINT "fk_profile__partner_7a6cd292";
ALTER TABLE "profile_courier" DROP COLUMN "partner_id";
