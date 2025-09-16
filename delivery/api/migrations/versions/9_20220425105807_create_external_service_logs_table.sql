-- upgrade --
CREATE TABLE IF NOT EXISTS "external_service_logs" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "service_name" VARCHAR(64) NOT NULL,
    "url" VARCHAR(256) NOT NULL,
    "request_body" JSONB,
    "response_body" JSONB,
    "status_code" INT NOT NULL,
    "owner" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "external_service_logs"."service_name" IS 'GBDFL: gbdfl, GBDUL: gbdul, BIOMETRY: biometry, STATE_BASE: state_base, SMS: sms';;
-- downgrade --
DROP TABLE IF EXISTS "external_service_logs";
