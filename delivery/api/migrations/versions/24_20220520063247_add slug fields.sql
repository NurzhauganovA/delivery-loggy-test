-- upgrade --
ALTER TABLE "deliverygraph" ADD "slug" VARCHAR(180) NOT NULL DEFAULT '';
ALTER TABLE "status" ADD "slug" VARCHAR(80) NOT NULL DEFAULT '';
-- downgrade --
ALTER TABLE "status" DROP COLUMN "slug";
ALTER TABLE "deliverygraph" DROP COLUMN "slug";
