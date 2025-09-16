-- upgrade --
ALTER TABLE "partner" ADD "type" VARCHAR(3) NOT NULL  DEFAULT 'too';
-- downgrade --
ALTER TABLE "partner" DROP COLUMN "type";