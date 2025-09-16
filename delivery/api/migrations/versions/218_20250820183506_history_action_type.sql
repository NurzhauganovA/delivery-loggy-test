-- upgrade --
ALTER TABLE "history" ADD IF NOT EXISTS "action_type" VARCHAR(30);
-- downgrade --
ALTER TABLE "history" DROP COLUMN IF EXISTS "action_type";
