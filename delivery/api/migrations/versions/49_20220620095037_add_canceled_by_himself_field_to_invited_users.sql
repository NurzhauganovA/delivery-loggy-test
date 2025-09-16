-- upgrade --
ALTER TABLE "invited_user" ADD "canceled_by_himself" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "invited_user" DROP COLUMN "canceled_by_himself";
