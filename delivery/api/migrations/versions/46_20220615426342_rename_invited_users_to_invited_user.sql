-- upgrade --
ALTER TABLE "invited_users" RENAME TO "invited_user";
-- downgrade --
ALTER TABLE "invited_user" RENAME TO "invited_users";