-- upgrade --
ALTER TABLE "item" ADD "accepted_delivery_statuses" varchar[];
ALTER TABLE "item" ADD "distribute" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "item" DROP COLUMN "accepted_delivery_statuses";
ALTER TABLE "item" DROP COLUMN "distribute";