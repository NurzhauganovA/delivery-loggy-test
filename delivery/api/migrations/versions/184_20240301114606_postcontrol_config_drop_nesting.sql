-- upgrade --
ALTER TABLE "postcontrol_configs" DROP CONSTRAINT "postcontrol_configs_parent_config_id_fkey";
ALTER TABLE "postcontrol_configs" DROP CONSTRAINT "postcontrol_configs_check";
UPDATE "postcontrol_configs" set "item_id"="parent"."item_id" FROM (SELECT "item_id", "id" FROM "postcontrol_configs") "parent" WHERE "parent_config_id"="parent"."id";
ALTER TABLE "postcontrol_configs" ALTER COLUMN "item_id" SET NOT NULL;
DROP INDEX "postcontrol_configs_u_together_item_id_name_partner_config_id";
DROP INDEX "postcontrol_configs_unique_together_item_id_name";
CREATE UNIQUE INDEX "postcontrol_configs_unique_together_item_id_name" on "postcontrol_configs" (item_id, name);
DROP INDEX "postcontrol_configs_unique_together_name_parent_config_id";
ALTER TABLE "postcontrol_configs" DROP COLUMN "parent_config_id";
-- downgrade --
ALTER TABLE "postcontrol_configs" ADD "parent_config_id" INT;
ALTER TABLE "postcontrol_configs" ALTER COLUMN "item_id" DROP NOT NULL;
ALTER TABLE "postcontrol_configs" ADD CONSTRAINT "postcontrol_configs_check" CHECK (("item_id" IS NOT NULL) OR ("parent_config_id" IS NOT NULL));
ALTER TABLE "postcontrol_configs" ADD CONSTRAINT "postcontrol_configs_parent_config_id_fkey" FOREIGN KEY ("parent_config_id") REFERENCES "postcontrol_configs" ("id") ON DELETE CASCADE;
CREATE UNIQUE INDEX postcontrol_configs_u_together_item_id_name_partner_config_id
    ON postcontrol_configs (item_id, name, parent_config_id)
    WHERE ((item_id IS NOT NULL) AND (parent_config_id IS NOT NULL));
DROP INDEX postcontrol_configs_unique_together_item_id_name;
CREATE UNIQUE INDEX postcontrol_configs_unique_together_item_id_name
    ON postcontrol_configs (item_id, name)
    WHERE ((item_id IS NOT NULL) AND (parent_config_id IS NULL));
CREATE UNIQUE INDEX postcontrol_configs_unique_together_name_parent_config_id
    ON postcontrol_configs (name, parent_config_id)
    WHERE ((item_id IS NULL) AND (parent_config_id IS NOT NULL));


