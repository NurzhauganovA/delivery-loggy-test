-- upgrade --
CREATE TABLE IF NOT EXISTS "courier_statistics" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "reaction_time" INTERVAL,
    "completion_time" INTERVAL,
    "order_count" SMALLINT NOT NULL  DEFAULT 0,
    "created_at" DATE NOT NULL,
    "courier_id" INT NOT NULL REFERENCES "profile_courier" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_courier_sta_courier_8135bd" UNIQUE ("courier_id", "created_at")
);
-- downgrade --
DROP TABLE IF EXISTS "courier_statistics";
