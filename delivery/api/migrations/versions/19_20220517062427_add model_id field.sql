-- upgrade --
ALTER TABLE "history" ADD "model_id" INT;
-- downgrade --
ALTER TABLE "history" DROP COLUMN "model_id";
