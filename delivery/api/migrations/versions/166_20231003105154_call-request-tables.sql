-- upgrade --
CREATE TABLE IF NOT EXISTS "call_requests" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "phone" VARCHAR(13) NOT NULL UNIQUE,
    "name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);;
CREATE TABLE IF NOT EXISTS "call_request_contacts" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "phone" VARCHAR(13) UNIQUE,
    "email" VARCHAR(255) UNIQUE,
    "name" VARCHAR(255) UNIQUE
);
-- downgrade --
DROP TABLE IF EXISTS "call_requests";
DROP TABLE IF EXISTS "call_request_contacts";
