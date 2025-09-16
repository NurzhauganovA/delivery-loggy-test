-- upgrade --
ALTER TABLE "deliverygraph" ADD "name" VARCHAR(128);
-- downgrade --
ALTER TABLE "deliverygraph" DROP COLUMN "name";
