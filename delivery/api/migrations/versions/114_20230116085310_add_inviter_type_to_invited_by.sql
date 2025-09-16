-- upgrade --
ALTER TABLE "invited_user" ADD "inviter_profile_type" VARCHAR(20) NOT NULL  DEFAULT 'service_manager';
-- downgrade --
ALTER TABLE "invited_user" DROP COLUMN "inviter_profile_type";
