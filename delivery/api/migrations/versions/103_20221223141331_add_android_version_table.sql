-- upgrade --
CREATE TABLE IF NOT EXISTS "android_version" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL UNIQUE DEFAULT 'x.x.x-LOGGY',
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
-- downgrade --
DROP TABLE IF EXISTS "android_version";
