-- upgrade --
UPDATE "revoked_token" SET "revoked_at"=CURRENT_TIMESTAMP WHERE "revoked_at" IS NULL;
ALTER TABLE "revoked_token" ALTER COLUMN "revoked_at" SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "revoked_token" ALTER COLUMN "revoked_at" SET NOT NULL;
-- downgrade --
ALTER TABLE "revoked_token" ALTER COLUMN "revoked_at" DROP NOT NULL;
ALTER TABLE "revoked_token" ALTER COLUMN "revoked_at" DROP DEFAULT;
