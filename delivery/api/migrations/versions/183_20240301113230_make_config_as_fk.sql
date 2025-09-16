-- upgrade --
ALTER TABLE "order.postcontrols" ALTER COLUMN "config_id" TYPE INT USING "config_id"::INT;
UPDATE "order.postcontrols" set "config_id"=NULL WHERE "config_id" NOT IN (SELECT "id" from "postcontrol_configs" WHERE "parent_config_id" IS NULL);
UPDATE "order.postcontrols" set "inner_param_id"=NULL WHERE "inner_param_id" NOT IN (SELECT "id" from "postcontrol_configs" WHERE "parent_config_id" IS NOT NULL);
UPDATE "order.postcontrols" set "inner_param_id"=NULL WHERE "config_id" NOT IN (SELECT "id" from "postcontrol_configs");
UPDATE "order.postcontrols" set "config_id"="inner_param_id" WHERE "inner_param_id" IS NOT NULL;
ALTER TABLE "order.postcontrols" ADD CONSTRAINT "fk_order.po_postcont_f6118820" FOREIGN KEY ("config_id") REFERENCES "postcontrol_configs" ("id") ON DELETE SET NULL;
ALTER TABLE "order.postcontrols" DROP COLUMN "inner_param_id";
-- downgrade --
ALTER TABLE "order.postcontrols" DROP CONSTRAINT "fk_order.po_postcont_f6118820";
ALTER TABLE "order.postcontrols" ADD "inner_param_id" INT;
ALTER TABLE "order.postcontrols" ALTER COLUMN "config_id" TYPE INT USING "config_id"::INT;
