-- upgrade --
CREATE TABLE IF NOT EXISTS "courier_devices" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "device_id" VARCHAR(500) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);;
-- downgrade --
DROP TABLE IF EXISTS "courier_devices";
