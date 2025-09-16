-- upgrade --
CREATE TABLE IF NOT EXISTS "partner.publicapitoken" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_expires" BOOL NOT NULL  DEFAULT False,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_partner.pub_partner_b283db" UNIQUE ("partner_id", "token")
);
-- downgrade --
DROP TABLE IF EXISTS "partner.publicapitoken";
