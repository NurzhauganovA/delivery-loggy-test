-- upgrade --
DROP INDEX "uid_city_name_dafd4b";
ALTER TABLE "city" ADD "country_id" INT;
UPDATE "city" SET "country_id"="region"."country_id" FROM (SELECT "id", "country_id" FROM "region") "region" WHERE "region"."id" = "region_id";
ALTER TABLE "city" ALTER COLUMN "country_id" SET NOT NULL;
CREATE UNIQUE INDEX "uid_city_name_6c965b" ON "city" ("name", "country_id");
ALTER TABLE "city" ADD CONSTRAINT "fk_city_country_f446f6f4" FOREIGN KEY ("country_id") REFERENCES "country" ("id") ON DELETE RESTRICT;
-- downgrade --
ALTER TABLE "city" DROP CONSTRAINT "fk_city_country_f446f6f4";
DROP INDEX "uid_city_name_6c965b";
ALTER TABLE "city" DROP COLUMN "country_id";
CREATE UNIQUE INDEX "uid_city_name_dafd4b" ON "city" ("name", "region_id");
