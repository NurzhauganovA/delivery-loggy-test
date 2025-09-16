-- upgrade --
ALTER TABLE "order_geolocations" ADD "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "order_geolocations" ADD "courier_id" INT NOT NULL;
ALTER TABLE "order_geolocations" ADD "speed" DECIMAL(5,2) NOT NULL  DEFAULT 0;
ALTER TABLE "order_geolocations" ADD "distance" DECIMAL(10,3) NOT NULL  DEFAULT 0;
ALTER TABLE "order_geolocations" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "order_geolocations" ALTER COLUMN "order_id" SET NOT NULL;
ALTER TABLE "order_geolocations" ADD CONSTRAINT "fk_order_ge_profile__ca1573bc" FOREIGN KEY ("courier_id") REFERENCES "profile_courier" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "order_geolocations" DROP CONSTRAINT "fk_order_ge_profile__ca1573bc";
ALTER TABLE "order_geolocations" DROP COLUMN "updated_at";
ALTER TABLE "order_geolocations" DROP COLUMN "courier_id";
ALTER TABLE "order_geolocations" DROP COLUMN "speed";
ALTER TABLE "order_geolocations" DROP COLUMN "distance";
ALTER TABLE "order_geolocations" DROP COLUMN "created_at";
ALTER TABLE "order_geolocations" ALTER COLUMN "order_id" DROP NOT NULL;
