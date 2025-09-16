-- upgrade --
CREATE TABLE IF NOT EXISTS "invited_users" (
    "phone_number" VARCHAR(12) NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "invited_by_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "invited_users";
