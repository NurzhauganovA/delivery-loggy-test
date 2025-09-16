-- upgrade --
ALTER TABLE "access_token" ADD "archived" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "access_token" DROP COLUMN "archived";
