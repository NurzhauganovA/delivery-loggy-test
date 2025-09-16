-- upgrade --
ALTER TABLE "invited_user" DROP COLUMN "status";
ALTER TABLE "profile_courier" ADD "status" VARCHAR(11) NOT NULL  DEFAULT 'invited';
-- downgrade --
ALTER TABLE "invited_user" ADD "status" VARCHAR(11) NOT NULL  DEFAULT 'invited';
ALTER TABLE "profile_courier" DROP COLUMN "status";
