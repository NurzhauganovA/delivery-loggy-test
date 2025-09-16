-- upgrade --
CREATE TABLE IF NOT EXISTS "ratings"
(
    "id"         SERIAL      NOT NULL PRIMARY KEY,
    "value"      SMALLINT    NOT NULL DEFAULT 100,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "courier_id" INT         NOT NULL REFERENCES "profile_courier" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX courier_monthly_rating
    ON "ratings" (
                  courier_id,
                  date(date_trunc('month', created_at AT TIME ZONE 'UTC'))
        );
-- downgrade --
DROP TABLE IF EXISTS "ratings";
