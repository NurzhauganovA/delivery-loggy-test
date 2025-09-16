-- upgrade --
CREATE TABLE IF NOT EXISTS "order_group_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "order_group_id" INT REFERENCES "order_group" ("id") ON DELETE SET NULL
);
-- downgrade --
DROP TABLE IF EXISTS "order_group_statuses";
