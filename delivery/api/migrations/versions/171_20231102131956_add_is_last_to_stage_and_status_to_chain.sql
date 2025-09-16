-- upgrade --
ALTER TABLE "order_chain" ADD "status" VARCHAR(11) NOT NULL  DEFAULT 'new';
ALTER TABLE "order_chain_stage" ADD "is_last" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "order_chain" DROP COLUMN "status";
ALTER TABLE "order_chain_stage" DROP COLUMN "is_last";
