-- upgrade --
ALTER TABLE "order" ADD "initial_delivery_datetime" TIMESTAMPTZ;;
UPDATE "order" SET "initial_delivery_datetime"="delivery_datetime" where "delivery_datetime" IS NOT NULL;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "initial_delivery_datetime";
