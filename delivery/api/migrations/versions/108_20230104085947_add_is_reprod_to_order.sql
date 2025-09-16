-- upgrade --
ALTER TABLE "order" ADD "is_preprod" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "is_preprod";
