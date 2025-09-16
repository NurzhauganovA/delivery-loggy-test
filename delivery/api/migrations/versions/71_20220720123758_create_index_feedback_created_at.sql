-- upgrade --
CREATE INDEX "idx_feedback_created_dfc56d" ON "feedback" ("created_at");
-- downgrade --
DROP INDEX "idx_feedback_created_dfc56d";
