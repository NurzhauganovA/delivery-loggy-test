-- upgrade --
ALTER TABLE "item" ADD "has_postcontrol" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "item" DROP COLUMN "has_postcontrol";
