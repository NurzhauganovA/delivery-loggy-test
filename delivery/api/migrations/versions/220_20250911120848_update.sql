-- upgrade --
ALTER TABLE "order" ADD "courier_service" VARCHAR(50);
ALTER TABLE "order" ADD "track_number" VARCHAR(255);
-- downgrade --
ALTER TABLE "order" DROP COLUMN "courier_service";
ALTER TABLE "order" DROP COLUMN "track_number";
