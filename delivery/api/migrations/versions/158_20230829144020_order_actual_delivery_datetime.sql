-- upgrade --
ALTER TABLE "order" ADD "actual_delivery_datetime" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "actual_delivery_datetime";
