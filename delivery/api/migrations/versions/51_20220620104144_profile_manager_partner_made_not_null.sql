-- upgrade --
DELETE FROM "profile_manager" WHERE partner_id IS NULL;
ALTER TABLE "profile_manager" ALTER COLUMN "partner_id" SET NOT NULL;
-- downgrade --
ALTER TABLE "profile_manager" ALTER COLUMN "partner_id" DROP NOT NULL;
