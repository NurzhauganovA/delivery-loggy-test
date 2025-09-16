-- upgrade --
ALTER TABLE "android_version" ADD "force_update" BOOL NOT NULL  DEFAULT True;
-- downgrade --
ALTER TABLE "android_version" DROP COLUMN "force_update";
