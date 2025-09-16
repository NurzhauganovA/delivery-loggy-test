-- upgrade --
ALTER TABLE "order" ADD "callbacks" JSONB NOT NULL default '{}'::JSONB;;
ALTER TABLE "order" DROP COLUMN "is_preprod";
-- downgrade --
ALTER TABLE "order" ADD "is_preprod" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "order" DROP COLUMN "callbacks";
