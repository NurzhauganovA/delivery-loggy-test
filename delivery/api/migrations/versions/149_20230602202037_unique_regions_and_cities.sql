-- upgrade --
CREATE UNIQUE INDEX "uid_city_name_dafd4b" ON "city" ("name", "region_id");
CREATE UNIQUE INDEX "uid_region_name_3588c0" ON "region" ("name", "country_id");
-- downgrade --
DROP INDEX "uid_region_name_3588c0";
DROP INDEX "uid_city_name_dafd4b";
