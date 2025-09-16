-- upgrade --
ALTER TABLE "status" ADD "code" VARCHAR(50)  UNIQUE;
-- downgrade --
ALTER TABLE "status" DROP COLUMN "code";
