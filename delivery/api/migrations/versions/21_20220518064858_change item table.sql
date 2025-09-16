-- upgrade --
ALTER TABLE "item" DROP COLUMN "courier_category";
ALTER TABLE "item" DROP COLUMN "transports";
ALTER TABLE "item" ALTER COLUMN "delivery_time" DROP NOT NULL;
-- downgrade --
ALTER TABLE "item" ADD "courier_category" VARCHAR(1) NOT NULL;
ALTER TABLE "item" ADD "transports" varchar[] NOT NULL;
ALTER TABLE "item" ALTER COLUMN "delivery_time" SET NOT NULL;
