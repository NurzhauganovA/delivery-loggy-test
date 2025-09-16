-- upgrade --
ALTER TABLE "invited_users" ADD "is_accepts" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "invited_users" DROP COLUMN "is_accepts";
