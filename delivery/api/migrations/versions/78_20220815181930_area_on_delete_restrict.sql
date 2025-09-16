-- upgrade --
ALTER TABLE "profile_courier" DROP CONSTRAINT "fk_profile__area_7e2fd544";
ALTER TABLE "profile_courier" ADD CONSTRAINT "fk_profile__area_8e3fd655" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE RESTRICT;

ALTER TABLE "order" DROP CONSTRAINT "fk_order_area_3d8a8896";
ALTER TABLE "order" ADD CONSTRAINT "fk_order_area_4d9a9907" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE RESTRICT;

ALTER TABLE "partner.shipment_points" DROP CONSTRAINT "fk_partner._area_8eae9cd1";
ALTER TABLE "partner.shipment_points" ADD CONSTRAINT "fk_partner._area_9eae0cd2" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE RESTRICT;
-- downgrade --
ALTER TABLE "profile_courier" DROP CONSTRAINT "fk_profile__area_8e3fd655";
ALTER TABLE "profile_courier" ADD CONSTRAINT "fk_profile__area_7e2fd544" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE CASCADE;

ALTER TABLE "order" DROP CONSTRAINT "fk_order_area_4d9a9907";
ALTER TABLE "order" ADD CONSTRAINT "fk_order_area_3d8a8896" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE CASCADE;

ALTER TABLE "partner.shipment_points" DROP CONSTRAINT "fk_partner._area_9eae0cd2";
ALTER TABLE "partner.shipment_points" ADD CONSTRAINT "fk_partner._area_8eae9cd1" FOREIGN KEY ("area_id") REFERENCES "area" ("id") ON DELETE CASCADE;
