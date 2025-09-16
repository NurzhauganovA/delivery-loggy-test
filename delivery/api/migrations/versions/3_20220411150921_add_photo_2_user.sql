-- upgrade --
ALTER TABLE "user" ADD "photo" TEXT;
-- downgrade --
ALTER TABLE "user" DROP COLUMN "photo";
