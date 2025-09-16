-- upgrade --
CREATE UNIQUE INDEX "uid_partner.shi_partner_943658" ON "partner.shipment_points" ("partner_id", "name");
CREATE UNIQUE INDEX "uid_partner.shi_partner_d49fa6" ON "partner.shipment_points" ("partner_id", "place_id");
-- downgrade --
DROP INDEX "uid_partner.shi_partner_d49fa6";
DROP INDEX "uid_partner.shi_partner_943658";
