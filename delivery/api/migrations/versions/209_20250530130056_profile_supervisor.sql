-- upgrade --
CREATE TABLE IF NOT EXISTS "profile_supervisor" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "country_id" INT NOT NULL REFERENCES "country" ("id") ON DELETE CASCADE,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL UNIQUE REFERENCES "user" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "profile_supervisor";
