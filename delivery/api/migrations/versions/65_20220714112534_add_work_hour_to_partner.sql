-- upgrade --
ALTER TABLE "partner" ADD "start_work_hour" VARCHAR(5);
ALTER TABLE "partner" ADD "end_work_hour" VARCHAR(5);
-- downgrade --
ALTER TABLE "partner" DROP COLUMN "start_work_hour";
ALTER TABLE "partner" DROP COLUMN "end_work_hour";
