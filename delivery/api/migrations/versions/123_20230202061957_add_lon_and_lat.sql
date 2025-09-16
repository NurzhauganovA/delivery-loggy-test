-- upgrade --
ALTER TABLE "city" ADD "longitude" DOUBLE PRECISION;
ALTER TABLE "city" ADD "latitude" DOUBLE PRECISION;
ALTER TABLE "city" ADD "timezone" VARCHAR(50);
-- downgrade --
ALTER TABLE "city" DROP COLUMN "longitude";
ALTER TABLE "city" DROP COLUMN "latitude";
ALTER TABLE "city" DROP COLUMN "timezone";
