-- upgrade --
ALTER TABLE "place" ALTER COLUMN "longitude" DROP NOT NULL;
ALTER TABLE "place" ALTER COLUMN "latitude" DROP NOT NULL;
-- downgrade --
ALTER TABLE "place" ALTER COLUMN "longitude" SET NOT NULL;
ALTER TABLE "place" ALTER COLUMN "latitude" SET NOT NULL;
