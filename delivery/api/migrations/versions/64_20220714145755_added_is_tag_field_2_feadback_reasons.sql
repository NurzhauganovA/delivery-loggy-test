-- upgrade --
ALTER TABLE "feedback_reason" ADD "is_tag" BOOL NOT NULL;
-- downgrade --
ALTER TABLE "feedback_reason" DROP COLUMN "is_tag";
