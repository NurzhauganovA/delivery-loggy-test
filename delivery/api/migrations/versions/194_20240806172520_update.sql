-- upgrade --
ALTER TABLE "history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
ALTER TABLE "order" ADD "manager" VARCHAR(255);
ALTER TABLE "order" ADD "idn" VARCHAR(255);
ALTER TABLE "order_chain_history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
ALTER TABLE "partner_shipment_point_history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
-- downgrade --
ALTER TABLE "order" DROP COLUMN "manager";
ALTER TABLE "order" DROP COLUMN "idn";
ALTER TABLE "history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
ALTER TABLE "order_chain_history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
ALTER TABLE "partner_shipment_point_history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
