-- upgrade --
ALTER TABLE "user" ADD "is_superuser" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "user" DROP COLUMN "is_superuser";
