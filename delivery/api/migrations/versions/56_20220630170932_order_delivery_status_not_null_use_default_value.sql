-- upgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_status" SET DEFAULT '{}'::jsonb;
ALTER TABLE "order" ALTER COLUMN "delivery_status" SET NOT NULL;
-- downgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_status" DROP NOT NULL;
ALTER TABLE "order" ALTER COLUMN "delivery_status" DROP DEFAULT;
