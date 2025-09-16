-- upgrade --
ALTER TABLE "history" ADD "initiator_role" VARCHAR(22);
-- downgrade --
ALTER TABLE "history" DROP COLUMN "initiator_role";
