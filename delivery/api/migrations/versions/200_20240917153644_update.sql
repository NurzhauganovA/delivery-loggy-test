-- upgrade --
ALTER TABLE "item" DROP COLUMN "name_kk";
ALTER TABLE "item" DROP COLUMN "name_en";
ALTER TABLE "item" DROP COLUMN "name_zh";
ALTER TABLE "item" DROP COLUMN "name_ru";
-- downgrade --
ALTER TABLE "item" ADD "name_kk" VARCHAR(255);
ALTER TABLE "item" ADD "name_en" VARCHAR(255);
ALTER TABLE "item" ADD "name_zh" VARCHAR(255);
ALTER TABLE "item" ADD "name_ru" VARCHAR(255);
