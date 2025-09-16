-- upgrade --
ALTER TABLE "external_service_history" ALTER COLUMN "service_name" TYPE VARCHAR(64) USING "service_name"::VARCHAR(64);
CREATE TABLE IF NOT EXISTS "firebase_devices" (
    "id" VARCHAR(1000) NOT NULL  PRIMARY KEY,
    "type" VARCHAR(1) NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "firebase_devices"."type" IS 'ANDROID: a, WEB: w, IOS: i';;
DROP TABLE IF EXISTS "courier_devices";
-- downgrade --
ALTER TABLE "external_service_history" ALTER COLUMN "service_name" TYPE VARCHAR(64) USING "service_name"::VARCHAR(64);
DROP TABLE IF EXISTS "firebase_devices";
