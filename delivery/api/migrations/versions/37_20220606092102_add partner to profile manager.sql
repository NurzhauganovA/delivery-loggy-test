-- upgrade --
ALTER TABLE "profile_manager" ADD "partner_id" INT;
ALTER TABLE "profile_manager" ADD CONSTRAINT "fk_profile__partner_d22c62f4" FOREIGN KEY ("partner_id") REFERENCES "partner" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "profile_manager" DROP CONSTRAINT "fk_profile__partner_d22c62f4";
ALTER TABLE "profile_manager" DROP COLUMN "partner_id";
