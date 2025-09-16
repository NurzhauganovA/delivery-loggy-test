-- upgrade --
ALTER TABLE "partner" DROP CONSTRAINT "partner_bin_key";
ALTER TABLE "partner" DROP CONSTRAINT "partner_name_en_key";
ALTER TABLE "partner" DROP CONSTRAINT "partner_name_kz_key";
ALTER TABLE "partner" DROP CONSTRAINT "partner_email_key";
ALTER TABLE "partner" DROP CONSTRAINT "partner_name_ru_key";
CREATE UNIQUE INDEX "partner_bin_key" ON "partner" ("bin", "courier_partner_id");
CREATE UNIQUE INDEX "partner_name_kz_key" ON "partner" ("name_kz", "courier_partner_id") where "name_kz" is not null;
CREATE UNIQUE INDEX "partner_name_ru_key" ON "partner" ("name_ru", "courier_partner_id") where "name_ru" is not null;
CREATE UNIQUE INDEX "partner_name_en_key" ON "partner" ("name_en", "courier_partner_id") where "name_en" is not null;
CREATE UNIQUE INDEX "partner_email_key" ON "partner" ("email", "courier_partner_id") where "email" is not null;
-- downgrade --
DROP INDEX "partner_bin_key";
DROP INDEX "partner_name_ru_key";
DROP INDEX "partner_email_key";
DROP INDEX "partner_name_en_key";
DROP INDEX "partner_name_kz_key";
ALTER TABLE "partner" ADD CONSTRAINT "partner_name_ru_key" UNIQUE("name_ru");
ALTER TABLE "partner" ADD CONSTRAINT "partner_email_key" UNIQUE("email");
ALTER TABLE "partner" ADD CONSTRAINT "partner_name_kz_key" UNIQUE("name_kz");
ALTER TABLE "partner" ADD CONSTRAINT "partner_name_en_key" UNIQUE("name_en");
ALTER TABLE "partner" ADD CONSTRAINT "partner_bin_key" UNIQUE("bin");
