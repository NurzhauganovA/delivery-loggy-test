-- upgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_status" TYPE VARCHAR(24) USING "delivery_status"::VARCHAR(24);
ALTER TABLE "profile_courier" ADD "state" VARCHAR(29);
-- downgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_status" TYPE VARCHAR(24) USING "delivery_status"::VARCHAR(24);
ALTER TABLE "profile_courier" DROP COLUMN "state";
