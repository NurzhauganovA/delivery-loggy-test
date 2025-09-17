-- upgrade --
ALTER TABLE "postcontrol_configs" ADD COLUMN IF NOT EXISTS "type" VARCHAR(18) NOT NULL DEFAULT 'post_control';
-- downgrade --
ALTER TABLE "postcontrol_configs" DROP COLUMN IF EXISTS "type";
