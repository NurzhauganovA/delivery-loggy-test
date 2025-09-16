-- upgrade --
ALTER TABLE "item" ADD "days_to_delivery" INT;
ALTER TABLE "partner_setting" DROP COLUMN "days_to_delivery";
-- downgrade --
ALTER TABLE "item" DROP COLUMN "days_to_delivery";
ALTER TABLE "partner_setting" ADD "days_to_delivery" INT;
