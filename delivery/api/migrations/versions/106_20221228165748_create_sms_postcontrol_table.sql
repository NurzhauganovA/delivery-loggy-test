-- upgrade --
CREATE TABLE IF NOT EXISTS "order_sms_postcontrols" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "otp" SMALLINT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "try_count" SMALLINT NOT NULL  DEFAULT 0,
    "accepted_at" TIMESTAMPTZ,
    "order_id" INT NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "order_sms_postcontrols";
