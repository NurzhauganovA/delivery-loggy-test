-- upgrade --
DELETE FROM "revoked_token" WHERE TRUE;
ALTER TABLE "revoked_token" ADD "exp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "revoked_token" ADD "client_id" INT NOT NULL DEFAULT 1;
ALTER TABLE "revoked_token" ADD CONSTRAINT "fk_revoked__user_96be3c59" FOREIGN KEY ("client_id") REFERENCES "user" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "revoked_token" DROP CONSTRAINT "fk_revoked__user_96be3c59";
ALTER TABLE "revoked_token" DROP COLUMN "exp";
ALTER TABLE "revoked_token" DROP COLUMN "client_id";
