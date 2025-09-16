-- upgrade --
ALTER TABLE "partner" ALTER COLUMN "affiliated" DROP NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "is_international" DROP NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "address" DROP NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "registration_date" DROP NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "name_kz" DROP NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "name_ru" DROP NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "activity_name_ru" DROP NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "is_commerce" DROP NOT NULL;
-- downgrade --
ALTER TABLE "partner" ALTER COLUMN "affiliated" SET NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "is_international" SET NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "address" SET NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "registration_date" SET NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "name_kz" SET NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "name_ru" SET NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "activity_name_ru" SET NOT NULL;
ALTER TABLE "partner" ALTER COLUMN "is_commerce" SET NOT NULL;
