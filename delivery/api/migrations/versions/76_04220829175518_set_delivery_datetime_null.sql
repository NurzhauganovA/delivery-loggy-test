-- upgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_datetime" DROP NOT NULL;
-- downgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_datetime" SET NOT NULL;