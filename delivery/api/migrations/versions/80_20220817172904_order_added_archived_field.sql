-- upgrade --
ALTER TABLE "order" ADD "archived" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "archived";
