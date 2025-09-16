-- upgrade --
ALTER TABLE "postcontrol_configs" ADD "parent_config_id" INT;
ALTER TABLE "postcontrol_configs" ADD CONSTRAINT "fk_postcont_postcont_331a2267" FOREIGN KEY ("parent_config_id") REFERENCES "postcontrol_configs" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "postcontrol_configs" DROP CONSTRAINT "fk_postcont_postcont_331a2267";
ALTER TABLE "postcontrol_configs" DROP COLUMN "parent_config_id";
