-- upgrade --
ALTER TABLE "order_group" ADD "accepted_by_courier_at" TIMESTAMPTZ;
ALTER TABLE "order_group" ADD "accepted_by_manager_at" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "order_group" DROP COLUMN "accepted_by_courier_at";
ALTER TABLE "order_group" DROP COLUMN "accepted_by_manager_at";
