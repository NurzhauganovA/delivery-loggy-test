-- upgrade --
ALTER TABLE "feedback" DROP COLUMN "auto_created";
ALTER TABLE "feedback" ALTER COLUMN "status" TYPE VARCHAR(20) USING "status"::VARCHAR(20);
ALTER TABLE "feedback" ALTER COLUMN "author_role" DROP DEFAULT;
ALTER TABLE "feedback" RENAME COLUMN "author_phone_number" TO "author_phone";
ALTER TABLE "feedback_reason" ADD "is_positive" BOOL NOT NULL;
ALTER TABLE "feedback_reason" ADD "rate" SMALLINT NOT NULL;
ALTER TABLE "feedback_reason" ALTER COLUMN "score" DROP DEFAULT;
ALTER TABLE "feedback_reason" ALTER COLUMN "reason" SET NOT NULL;
ALTER TABLE "feedback_reason" ALTER COLUMN "partner_id" DROP NOT NULL;
-- downgrade --
ALTER TABLE "feedback" ADD "auto_created" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "feedback" ALTER COLUMN "status" TYPE VARCHAR(20) USING "status"::VARCHAR(20);
ALTER TABLE "feedback" ALTER COLUMN "author_role" SET DEFAULT 'system';
ALTER TABLE "feedback" RENAME COLUMN "author_phone" TO "author_phone_number";
ALTER TABLE "feedback_reason" DROP COLUMN "is_positive";
ALTER TABLE "feedback_reason" DROP COLUMN "rate";
ALTER TABLE "feedback_reason" ALTER COLUMN "score" SET DEFAULT 0;
ALTER TABLE "feedback_reason" ALTER COLUMN "reason" DROP NOT NULL;
ALTER TABLE "feedback_reason" ALTER COLUMN "partner_id" SET NOT NULL;