-- upgrade --
ALTER TABLE "invited_user" RENAME COLUMN "invited_by_id" TO "inviter_id";
ALTER TABLE "invited_user" ADD CONSTRAINT "fk_invited__user_0d3f8aea" FOREIGN KEY ("inviter_id") REFERENCES "user" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "invited_user" RENAME COLUMN "inviter_id" TO "invited_by_id";
ALTER TABLE "invited_user" ADD CONSTRAINT "fk_invited__user_b4c67d6f" FOREIGN KEY ("invited_by_id") REFERENCES "user" ("id") ON DELETE CASCADE;
