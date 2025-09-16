-- upgrade --
ALTER TABLE "order" ADD "postcontrol_configs" JSONB NOT NULL DEFAULT '[]'::JSON;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "postcontrol_configs";
