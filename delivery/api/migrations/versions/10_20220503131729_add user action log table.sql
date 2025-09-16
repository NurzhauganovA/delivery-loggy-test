-- upgrade --
CREATE TABLE IF NOT EXISTS "useractionlogs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "request_method" VARCHAR(7) NOT NULL,
    "model_type" VARCHAR(50) NOT NULL,
    "action_data" JSONB,
    "initiator_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "useractionlogs"."request_method" IS 'GET: GET, POST: POST, PUT: PUT, DELETE: DELETE, PATCH: PATCH, HEAD: HEAD, OPTIONS: OPTIONS';
-- downgrade --
DROP TABLE IF EXISTS "useractionlogs";
