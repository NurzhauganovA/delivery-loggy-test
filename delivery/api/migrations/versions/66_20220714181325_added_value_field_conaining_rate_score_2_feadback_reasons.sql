-- upgrade --
ALTER TABLE "feedback" ADD "rate" SMALLINT NOT NULL;
ALTER TABLE "feedback_reason" RENAME COLUMN "reason" TO "name";
ALTER TABLE "feedback_reason" ADD "value" JSONB NOT NULL;
ALTER TABLE "feedback_reason" DROP COLUMN "rate";
ALTER TABLE "feedback_reason" DROP COLUMN "is_positive";
ALTER TABLE "feedback_reason" DROP COLUMN "score";
-- downgrade --
ALTER TABLE "feedback" DROP COLUMN "rate";
ALTER TABLE "feedback_reason" RENAME COLUMN "name" TO "reason";
ALTER TABLE "feedback_reason" ADD "rate" SMALLINT NOT NULL;
ALTER TABLE "feedback_reason" ADD "is_positive" BOOL NOT NULL;
ALTER TABLE "feedback_reason" ADD "score" SMALLINT NOT NULL;
ALTER TABLE "feedback_reason" DROP COLUMN "value";
