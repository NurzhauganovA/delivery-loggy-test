-- upgrade --
ALTER TABLE "revoked_token" DROP CONSTRAINT "revoked_token_client_id_fkey";
ALTER TABLE "access_token" DROP CONSTRAINT "access_token_client_id_fkey";
ALTER TABLE "access_token" DROP COLUMN "client_id";
ALTER TABLE "access_token" DROP COLUMN "issued_at";
ALTER TABLE "access_token" ALTER COLUMN "token" TYPE VARCHAR(9000) USING "token"::VARCHAR(9000);
ALTER TABLE "refresh_token" DROP COLUMN "issued_at";
ALTER TABLE "revoked_token" DROP COLUMN "client_id";
-- downgrade --
ALTER TABLE "access_token" ADD "client_id" INT NOT NULL DEFAULT 1;
ALTER TABLE "access_token" ADD "issued_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "access_token" ALTER COLUMN "token" TYPE VARCHAR(255) USING "token"::VARCHAR(255);
ALTER TABLE "refresh_token" ADD "issued_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "revoked_token" ADD "client_id" INT NOT NULL DEFAULT 1;
ALTER TABLE "access_token" ADD CONSTRAINT "revoked_token_client_id_fkey" FOREIGN KEY ("client_id") REFERENCES "user" ("id") ON DELETE CASCADE;
ALTER TABLE "revoked_token" ADD CONSTRAINT "revoked_token_client_id_fkey" FOREIGN KEY ("client_id") REFERENCES "user" ("id") ON DELETE CASCADE;
