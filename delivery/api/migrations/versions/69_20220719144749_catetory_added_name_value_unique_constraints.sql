-- upgrade --
ALTER TABLE "categories" DROP CONSTRAINT "categories_name_key";
ALTER TABLE "categories" ADD CONSTRAINT "categories_partner_item_type_name_uniq" UNIQUE ("partner_id", "item_type", "name");
ALTER TABLE "categories" ADD CONSTRAINT "categories_partner_item_type_value_uniq" UNIQUE ("partner_id", "item_type", "value");
-- downgrade --
ALTER TABLE "categories" DROP CONSTRAINT "categories_partner_item_type_name_uniq";
ALTER TABLE "categories" DROP CONSTRAINT "categories_partner_item_type_value_uniq";
ALTER TABLE "categories" ADD CONSTRAINT "categories_name_key" UNIQUE ("name");
