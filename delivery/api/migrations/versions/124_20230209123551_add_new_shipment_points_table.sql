-- upgrade --
alter table "partner.shipment_points" rename to "partner_shipment_point";
ALTER TABLE "partner_shipment_point" ADD "address" VARCHAR(255) NULL;
ALTER TABLE "partner_shipment_point" ADD "latitude" DECIMAL(10,8);
ALTER TABLE "partner_shipment_point" ADD "longitude" DECIMAL(11,8);
ALTER TABLE "partner_shipment_point" ADD "city_id" INT;
ALTER TABLE "partner_shipment_point" ADD CONSTRAINT "fk_partner._city_021ab3ed" FOREIGN KEY ("city_id") REFERENCES "city" ("id") ON DELETE SET NULL;
ALTER TABLE "partner_shipment_point" ADD CONSTRAINT "unique_name_and_city_id" UNIQUE (name, city_id, partner_id);
UPDATE partner_shipment_point
SET latitude=subquery.latitude,
    longitude=subquery.longitude,
    address=subquery.address,
    city_id=subquery.city_id
FROM (select id, latitude, longitude, address, city_id from place) AS subquery
WHERE partner_shipment_point.place_id=subquery.id;
ALTER TABLE "partner_shipment_point" drop column "place_id";
ALTER TABLE "partner_shipment_point" drop column "area_id";
-- downgrade --
alter table "partner_shipment_point" rename to "partner.shipment_points";
ALTER TABLE "partner.shipment_points" DROP CONSTRAINT "fk_partner._city_021ab3ed";
ALTER TABLE "partner.shipment_points" DROP COLUMN "latitude";
ALTER TABLE "partner.shipment_points" DROP COLUMN "longitude";
ALTER TABLE "partner.shipment_points" DROP COLUMN "city_id";
ALTER TABLE "partner.shipment_points" DROP COLUMN "address";