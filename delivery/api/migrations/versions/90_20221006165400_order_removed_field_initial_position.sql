-- upgrade --
ALTER TABLE "order" DROP COLUMN "initial_position";
-- downgrade --
ALTER TABLE "order" ADD "initial_position" INT;
