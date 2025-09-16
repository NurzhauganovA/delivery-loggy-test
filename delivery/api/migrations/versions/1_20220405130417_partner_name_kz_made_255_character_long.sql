-- upgrade --
ALTER TABLE "partner" ALTER COLUMN "name_kz" TYPE VARCHAR(255) USING "name_kz"::VARCHAR(255);
-- downgrade --
ALTER TABLE "partner" ALTER COLUMN "name_kz" TYPE VARCHAR(64) USING "name_kz"::VARCHAR(64);
