-- upgrade --
ALTER TABLE "order" DROP COLUMN "postcontrol_configs";
-- downgrade --
ALTER TABLE "order" ADD "postcontrol_configs" JSONB NOT NULL DEFAULT '[]'::JSONB;
