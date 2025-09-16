-- upgrade --
ALTER TABLE "order" DROP COLUMN "is_shown";
-- downgrade --
ALTER TABLE "order" ADD "is_shown" BOOL NOT NULL  DEFAULT False;
