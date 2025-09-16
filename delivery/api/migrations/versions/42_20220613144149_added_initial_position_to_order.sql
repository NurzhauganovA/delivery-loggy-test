-- upgrade --
ALTER TABLE "order" ADD "initial_position" int NULL;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "initial_position";