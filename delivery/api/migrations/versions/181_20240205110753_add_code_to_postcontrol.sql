-- upgrade --
ALTER TABLE "order.postcontrols" ADD "code" VARCHAR(255);
ALTER TABLE "postcontrol_configs" ADD "code" VARCHAR(255);
-- downgrade --
ALTER TABLE "order.postcontrols" DROP COLUMN "code";
ALTER TABLE "postcontrol_configs" DROP COLUMN "code";
