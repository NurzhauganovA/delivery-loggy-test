-- upgrade --
ALTER TABLE "access_token" DROP COLUMN "revoked_at";
ALTER TABLE "access_token" DROP COLUMN "is_revoked";
CREATE TABLE IF NOT EXISTS "revoked_token" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token" VARCHAR(255) NOT NULL UNIQUE,
    "revoked_at" TIMESTAMPTZ,
    "client_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_revoked_tok_client__6bcae0" ON "revoked_token" ("client_id");-- downgrade --
ALTER TABLE "access_token" ADD "revoked_at" TIMESTAMPTZ;
ALTER TABLE "access_token" ADD "is_revoked" BOOL NOT NULL  DEFAULT 'false';
DROP TABLE IF EXISTS "revoked_token";
