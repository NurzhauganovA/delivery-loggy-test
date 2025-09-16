-- upgrade --
ALTER TABLE "partner.shipment_points" ADD "area_id" INT;
ALTER TABLE "partner.shipment_points" ADD CONSTRAINT "fk_partner._area_8eae9cd1" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "partner.shipment_points" DROP CONSTRAINT "fk_partner._area_8eae9cd1";
ALTER TABLE "partner.shipment_points" DROP COLUMN "area_id";
