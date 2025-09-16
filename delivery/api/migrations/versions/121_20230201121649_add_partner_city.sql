-- upgrade --
CREATE TABLE IF NOT EXISTS "partners_cities" (
    "city_id" INT NOT NULL REFERENCES "city" ("id") ON DELETE CASCADE,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "partners_cities";