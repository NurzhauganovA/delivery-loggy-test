-- upgrade --
ALTER TABLE "user" ADD "personal_agreement" TEXT;
-- downgrade --
ALTER TABLE "user" DROP COLUMN "personal_agreement";
