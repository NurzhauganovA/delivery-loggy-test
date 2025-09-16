-- upgrade --
ALTER TABLE "order_pan" ADD "pan_suffix" VARCHAR(4);
-- downgrade --
ALTER TABLE "order_pan" DROP COLUMN "pan_suffix";
