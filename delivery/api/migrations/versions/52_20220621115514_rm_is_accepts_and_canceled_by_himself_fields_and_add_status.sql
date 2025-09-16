-- upgrade --
ALTER TABLE "invited_user" DROP COLUMN "canceled_by_himself";
ALTER TABLE "invited_user" DROP COLUMN "is_accepts";
DELETE FROM "invited_user";
ALTER TABLE "invited_user" ADD "status" VARCHAR(11) NOT NULL;
-- downgrade --
ALTER TABLE "invited_user" ADD "canceled_by_himself" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "invited_user" ADD "is_accepts" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "invited_user" DROP COLUMN "status";
