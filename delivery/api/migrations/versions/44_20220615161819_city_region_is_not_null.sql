-- upgrade --
ALTER TABLE "city" ALTER COLUMN "region_id" SET NOT NULL;
-- downgrade --
ALTER TABLE "city" ALTER COLUMN "region_id" DROP NOT NULL;
