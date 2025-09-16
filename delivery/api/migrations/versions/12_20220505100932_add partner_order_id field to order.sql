-- upgrade --
ALTER TABLE "order" ADD "partner_order_id" VARCHAR(255);
-- downgrade --
ALTER TABLE "order" DROP COLUMN "partner_order_id";
