-- upgrade --
ALTER TABLE "external_service_history" ADD "owner_id" INT;
ALTER TABLE "external_service_history" DROP COLUMN "owner";
ALTER TABLE "external_service_history" ADD CONSTRAINT "fk_external_user_87d53d16" FOREIGN KEY ("owner_id") REFERENCES "user" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "external_service_history" DROP CONSTRAINT "fk_external_user_87d53d16";
ALTER TABLE "external_service_history" ADD "owner" JSONB;
ALTER TABLE "external_service_history" DROP COLUMN "owner_id";
