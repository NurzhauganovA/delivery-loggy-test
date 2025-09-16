-- upgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_status" TYPE JSONB USING json_build_object('status', delivery_status)::JSONB;
-- downgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_status" TYPE VARCHAR(24) USING "delivery_status"::VARCHAR(24);
