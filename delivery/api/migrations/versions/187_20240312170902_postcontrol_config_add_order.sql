-- upgrade --
ALTER TABLE "postcontrol_configs" ADD "order" SMALLINT NOT NULL  DEFAULT 1;
-- downgrade --
ALTER TABLE "postcontrol_configs" DROP COLUMN "order";
