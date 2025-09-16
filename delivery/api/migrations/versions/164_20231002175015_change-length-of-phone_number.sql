-- upgrade --
ALTER TABLE "user" ALTER COLUMN "phone_number" TYPE VARCHAR(13) USING "phone_number"::VARCHAR(13);
-- downgrade --
ALTER TABLE "user" ALTER COLUMN "phone_number" TYPE VARCHAR(12) USING "phone_number"::VARCHAR(12);
