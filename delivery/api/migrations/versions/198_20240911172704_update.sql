-- upgrade --
ALTER TABLE "country" ADD "name_kk" VARCHAR(255)  UNIQUE;
ALTER TABLE "deliverygraph" ADD "name_kk" VARCHAR(128);
ALTER TABLE "partner" ADD "name_zh" VARCHAR(255);
ALTER TABLE "partner" RENAME COLUMN "name_kz" TO "name_kk";
ALTER TABLE "status" ADD "name_kk" VARCHAR(50);
ALTER TABLE "city" ADD "name_kk" VARCHAR(255);
-- downgrade --
ALTER TABLE "city" DROP COLUMN "name_kk";
ALTER TABLE "status" DROP COLUMN "name_kk";
ALTER TABLE "country" DROP COLUMN "name_kk";
ALTER TABLE "partner" DROP COLUMN "name_zh";
ALTER TABLE "partner" RENAME COLUMN "name_kk" TO "name_kz";
ALTER TABLE "deliverygraph" DROP COLUMN "name_kk";
