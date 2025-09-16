-- upgrade --
DROP TABLE IF EXISTS "profile_dispatcher_city";
CREATE TABLE "profile_dispatcher_partner" ("partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE,"profile_dispatcher_id" INT NOT NULL REFERENCES "profile_dispatcher" ("id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "profile_dispatcher_partner";
CREATE TABLE "profile_dispatcher_city" ("city_id" INT NOT NULL REFERENCES "city" ("id") ON DELETE CASCADE,"profile_dispatcher_id" INT NOT NULL REFERENCES "profile_dispatcher" ("id") ON DELETE CASCADE);
