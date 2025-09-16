-- upgrade --
ALTER TABLE "profile_branch_manager" DROP COLUMN "city_id";
CREATE TABLE "profile_branch_manager_city" ("city_id" INT NOT NULL REFERENCES "city" ("id") ON DELETE CASCADE,"profile_branch_manager_id" INT NOT NULL REFERENCES "profile_branch_manager" ("id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "profile_branch_manager_city";
ALTER TABLE "profile_branch_manager" ADD "city_id" INT NOT NULL;
ALTER TABLE "profile_branch_manager" ADD CONSTRAINT "fk_profile__city_4f1dac29" FOREIGN KEY ("city_id") REFERENCES "city" ("id") ON DELETE CASCADE;
