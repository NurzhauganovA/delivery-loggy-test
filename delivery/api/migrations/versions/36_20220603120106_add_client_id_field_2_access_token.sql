-- upgrade --
DELETE FROM "access_token";
ALTER TABLE "access_token" ADD "client_id" INT NOT NULL;
ALTER TABLE "access_token" ADD CONSTRAINT "fk_access_t_user_814154ca" FOREIGN KEY ("client_id") REFERENCES "user" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "access_token" DROP CONSTRAINT "fk_access_t_user_814154ca";
ALTER TABLE "access_token" DROP COLUMN "client_id";
