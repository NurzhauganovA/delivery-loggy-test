-- upgrade --
ALTER TABLE "postcontrol_configs" ADD "type" VARCHAR(18) NOT NULL  DEFAULT 'post_control';
-- downgrade --
ALTER TABLE "postcontrol_configs" DROP COLUMN "type";
