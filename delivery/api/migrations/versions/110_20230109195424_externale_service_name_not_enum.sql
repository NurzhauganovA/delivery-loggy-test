-- upgrade --
ALTER TABLE "external_service_history" ALTER COLUMN "service_name" TYPE VARCHAR(64) USING "service_name"::VARCHAR(64);
-- downgrade --
ALTER TABLE "external_service_history" ALTER COLUMN "service_name" TYPE VARCHAR(64) USING "service_name"::VARCHAR(64);
