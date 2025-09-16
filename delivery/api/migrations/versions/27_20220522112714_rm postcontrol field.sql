-- upgrade --
ALTER TABLE "item" DROP COLUMN "post_control";
-- downgrade --
ALTER TABLE "item" ADD "post_control" BOOL NOT NULL  DEFAULT False;
