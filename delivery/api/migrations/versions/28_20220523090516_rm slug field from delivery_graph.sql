-- upgrade --
ALTER TABLE "deliverygraph" DROP COLUMN "slug";
-- downgrade --
ALTER TABLE "deliverygraph" ADD "slug" VARCHAR(180) NOT NULL;
