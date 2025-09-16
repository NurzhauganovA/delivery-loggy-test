-- upgrade --
ALTER TABLE "partner_setting" ADD COLUMN IF NOT EXISTS "default_order_group_couriers" JSONB DEFAULT '{}'::JSONB;
-- downgrade --
ALTER TABLE "partner_setting" DROP COLUMN "default_order_group_couriers";
