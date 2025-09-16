-- upgrade --
CREATE TABLE IF NOT EXISTS "profile_general_call_center_manager" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL UNIQUE REFERENCES "user" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "profile_general_call_center_manager";
