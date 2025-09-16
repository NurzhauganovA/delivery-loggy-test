-- upgrade --
ALTER TABLE "item" ADD "message_for_noncall" TEXT;
-- downgrade --
ALTER TABLE "item" DROP COLUMN "message_for_noncall";
