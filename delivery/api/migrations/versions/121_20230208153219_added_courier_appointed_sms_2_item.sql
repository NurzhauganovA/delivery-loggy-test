-- upgrade --
ALTER TABLE "item" ADD "courier_appointed_sms_on" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "item" ADD "courier_appointed_sms" TEXT;
-- downgrade --
ALTER TABLE "item" DROP COLUMN "courier_appointed_sms_on";
ALTER TABLE "item" DROP COLUMN "courier_appointed_sms";
