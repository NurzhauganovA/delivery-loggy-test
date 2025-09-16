-- upgrade --
ALTER TABLE "partner" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "user" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
-- downgrade --
ALTER TABLE "user" DROP COLUMN "created_at";
ALTER TABLE "partner" DROP COLUMN "created_at";
