-- upgrade --
CREATE UNIQUE INDEX "uid_item_cities_city_id_147e6e" ON "item_cities" ("city_id", "item_id");
CREATE UNIQUE INDEX "uid_item_shipme_item_id_c51dcb" ON "item_shipment_points" ("item_id", "shipment_point_id");
-- downgrade --
DROP INDEX "uid_item_shipme_item_id_c51dcb";
DROP INDEX "uid_item_cities_city_id_147e6e";
