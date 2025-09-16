-- upgrade --
ALTER TABLE "user" ADD "email" VARCHAR(50)  UNIQUE;
-- downgrade --
ALTER TABLE "user" DROP COLUMN "email";
