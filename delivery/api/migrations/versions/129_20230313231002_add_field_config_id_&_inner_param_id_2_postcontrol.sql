-- upgrade --
ALTER TABLE "order.postcontrols" ADD "send" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "order.postcontrols" ADD "config_id" INT;
ALTER TABLE "order.postcontrols" ADD "inner_param_id" INT;
-- downgrade --
ALTER TABLE "order.postcontrols" DROP COLUMN "send";
ALTER TABLE "order.postcontrols" DROP COLUMN "config_id";
ALTER TABLE "order.postcontrols" DROP COLUMN "inner_param_id";
