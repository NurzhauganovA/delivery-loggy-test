-- upgrade --
ALTER TABLE "partner_setting" ADD "default_order_group_courier_id" INT;
ALTER TABLE "partner_setting" ADD CONSTRAINT "fk_partner__profile__db6eaea6" FOREIGN KEY ("default_order_group_courier_id") REFERENCES "profile_courier" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "partner_setting" DROP CONSTRAINT "fk_partner__profile__db6eaea6";
ALTER TABLE "partner_setting" DROP COLUMN "default_order_group_courier_id";