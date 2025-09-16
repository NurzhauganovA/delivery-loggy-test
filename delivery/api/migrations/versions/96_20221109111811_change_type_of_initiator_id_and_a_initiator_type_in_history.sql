-- upgrade --
ALTER TABLE "history" ADD "initiator_type" VARCHAR(15) NOT NULL DEFAULT 'User';
-- downgrade --
ALTER TABLE "history" DROP COLUMN "initiator_type";