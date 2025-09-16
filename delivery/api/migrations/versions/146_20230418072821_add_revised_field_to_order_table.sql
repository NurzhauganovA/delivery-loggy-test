-- upgrade --
ALTER TABLE "order" ADD "revised" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "revised";
