-- upgrade --
ALTER TABLE "feedback" ALTER COLUMN "order_id" SET NOT NULL;
-- downgrade --
ALTER TABLE "feedback" ALTER COLUMN "order_id" DROP NOT NULL;
