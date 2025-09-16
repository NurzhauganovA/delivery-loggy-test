-- upgrade --
CREATE UNIQUE INDEX "uid_partners_ci_partner_f29d25" ON "partners_cities" ("partner_id", "city_id");
-- downgrade --
DROP INDEX "uid_partners_ci_partner_f29d25";
