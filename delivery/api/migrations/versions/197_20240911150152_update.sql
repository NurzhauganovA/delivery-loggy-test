-- upgrade --
ALTER TABLE "country" ADD "name_en" VARCHAR(255)  UNIQUE;
ALTER TABLE "country" ADD "name_zh" VARCHAR(255)  UNIQUE;
ALTER TABLE "country" ADD "name_ru" VARCHAR(255) UNIQUE;
ALTER TABLE "deliverygraph" ADD "name_en" VARCHAR(128);
ALTER TABLE "deliverygraph" ADD "name_zh" VARCHAR(128);
ALTER TABLE "deliverygraph" ADD "name_ru" VARCHAR(128);
ALTER TABLE "status" ADD "name_en" VARCHAR(50);
ALTER TABLE "status" ADD "name_zh" VARCHAR(50);
ALTER TABLE "status" ADD "name_ru" VARCHAR(50);
ALTER TABLE "city" ADD "name_en" VARCHAR(255);
ALTER TABLE "city" ADD "name_zh" VARCHAR(255);
ALTER TABLE "city" ADD "name_ru" VARCHAR(255);
-- downgrade --
ALTER TABLE "city" DROP COLUMN "name_en";
ALTER TABLE "city" DROP COLUMN "name_zh";
ALTER TABLE "city" DROP COLUMN "name_ru";
ALTER TABLE "status" DROP COLUMN "name_en";
ALTER TABLE "status" DROP COLUMN "name_zh";
ALTER TABLE "status" DROP COLUMN "name_ru";
ALTER TABLE "country" DROP COLUMN "name_en";
ALTER TABLE "country" DROP COLUMN "name_zh";
ALTER TABLE "country" DROP COLUMN "name_ru";
ALTER TABLE "deliverygraph" DROP COLUMN "name_en";
ALTER TABLE "deliverygraph" DROP COLUMN "name_zh";
ALTER TABLE "deliverygraph" DROP COLUMN "name_ru";
