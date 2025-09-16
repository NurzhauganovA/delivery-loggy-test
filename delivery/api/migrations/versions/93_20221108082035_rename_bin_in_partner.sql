-- upgrade --
ALTER TABLE "partner" RENAME COLUMN "bin" TO "identifier";
-- downgrade --
ALTER TABLE "partner" RENAME COLUMN "identifier" TO "bin";
