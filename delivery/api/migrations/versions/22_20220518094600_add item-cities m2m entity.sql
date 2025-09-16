-- upgrade --
CREATE TABLE IF NOT EXISTS "item_cities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "city_id" INT NOT NULL REFERENCES "city" ("id") ON DELETE CASCADE,
    "item_id" INT NOT NULL REFERENCES "item" ("id") ON DELETE CASCADE
);
ALTER TABLE "item" DROP COLUMN "city_id";
-- downgrade --
DROP TABLE IF EXISTS "item_cities";
ALTER TABLE "item" ADD "city_id" INT NULL REFERENCES "city" ON DELETE CASCADE;
