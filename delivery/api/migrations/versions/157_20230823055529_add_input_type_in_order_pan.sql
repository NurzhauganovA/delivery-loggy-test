-- upgrade --
ALTER TABLE "order_pan" ADD "input_type" VARCHAR(8);
-- downgrade --
ALTER TABLE "order_pan" DROP COLUMN "input_type";
