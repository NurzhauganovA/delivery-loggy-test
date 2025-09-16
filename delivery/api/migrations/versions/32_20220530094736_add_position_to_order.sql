-- upgrade --
ALTER TABLE "order" ADD "position" INT;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "position";
