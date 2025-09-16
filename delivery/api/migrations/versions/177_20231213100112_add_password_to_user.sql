-- upgrade --
ALTER TABLE "user" ADD "password" VARCHAR(500);
-- downgrade --
ALTER TABLE "user" DROP COLUMN "password";
