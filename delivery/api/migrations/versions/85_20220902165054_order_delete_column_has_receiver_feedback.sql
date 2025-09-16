-- upgrade --
ALTER TABLE "order" DROP COLUMN "has_receiver_feedback";
-- downgrade --
ALTER TABLE "order" ADD "has_receiver_feedback" BOOL NOT NULL  DEFAULT False;
