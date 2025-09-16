-- upgrade --
CREATE TABLE IF NOT EXISTS "groups" (
    "slug" VARCHAR(40) NOT NULL  PRIMARY KEY
);;
CREATE TABLE IF NOT EXISTS "permissions" (
    "slug" VARCHAR(10) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE
);;
CREATE TABLE "user_permissions" ("user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,"permission_id" VARCHAR(10) NOT NULL REFERENCES "permissions" ("slug") ON DELETE CASCADE);
ALTER TABLE "user_permissions" ADD CONSTRAINT "user_permission_unique" UNIQUE ("user_id", "permission_id");
CREATE TABLE "groups_user" ("user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,"groups_id" VARCHAR(40) NOT NULL REFERENCES "groups" ("slug") ON DELETE CASCADE);
ALTER TABLE "groups_user" ADD CONSTRAINT "groups_user_unique" UNIQUE ("groups_id", "user_id");
CREATE TABLE "groups_permissions" ("groups_id" VARCHAR(40) NOT NULL REFERENCES "groups" ("slug") ON DELETE CASCADE, "permission_id" VARCHAR(10) NOT NULL REFERENCES "permissions" ON DELETE CASCADE);
ALTER TABLE "groups_permissions" ADD CONSTRAINT "groups_permission_unique" UNIQUE ("groups_id", "permission_id");
-- downgrade --
DROP TABLE IF EXISTS "groups_user" CASCADE;
DROP TABLE IF EXISTS "groups" CASCADE;
DROP TABLE IF EXISTS "permissions" CASCADE;
DROP TABLE IF EXISTS "groups_permissions" CASCADE;
DROP TABLE IF EXISTS "user_permissions" CASCADE;
