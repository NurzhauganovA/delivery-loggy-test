-- upgrade --
ALTER TABLE "history" DROP CONSTRAINT "history_initiator_id_fkey";
ALTER TABLE "history" ALTER COLUMN "initiator_id" DROP NOT NULL;
ALTER TABLE "history" ALTER COLUMN "initiator_id" TYPE INT USING "initiator_id"::INT;
-- downgrade --
ALTER TABLE "history" ALTER COLUMN "initiator_id" SET NOT NULL;
ALTER TABLE "history" ALTER COLUMN "initiator_id" TYPE INT USING "initiator_id"::INT;
ALTER TABLE "history" ADD CONSTRAINT "history_initiator_id_fkey" FOREIGN KEY ("initiator_id") REFERENCES "user" ("id") ON DELETE CASCADE;
