-- upgrade --
ALTER TABLE "profile_owner" ADD CONSTRAINT "profile_owner_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
ALTER TABLE "profile_owner" ADD CONSTRAINT "profile_owner_partner_id_fkey" FOREIGN KEY ("partner_id") REFERENCES "partner" ("id") ON DELETE CASCADE;
ALTER TABLE "profile_courier" ADD CONSTRAINT "profile_courier_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
ALTER TABLE "profile_manager" ADD CONSTRAINT "profile_manager_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
ALTER TABLE "profile_dispatcher" ADD CONSTRAINT "profile_dispatcher_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
ALTER TABLE "profile_service_manager" ADD CONSTRAINT "profile_service_manager_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "profile_branch_manager" DROP CONSTRAINT "profile_branch_manager_user_id_fkey";
ALTER TABLE "profile_owner" DROP CONSTRAINT "profile_owner_user_id_fkey";
ALTER TABLE "profile_courier" DROP CONSTRAINT  "profile_courier_user_id_fkey";
ALTER TABLE "profile_dispatcher" DROP CONSTRAINT  "profile_dispatcher_user_id_fkey";
ALTER TABLE "profile_manager" DROP CONSTRAINT "profile_manager_user_id_fkey";
ALTER TABLE "profile_service_manager" DROP CONSTRAINT "profile_service_manager_user_id_fkey";
