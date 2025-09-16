-- upgrade --
ALTER TABLE "deliverygraph" ADD "slug" VARCHAR(80) NULL;
-- downgrade --
ALTER TABLE "deliverygraph" DROP COLUMN "slug";
