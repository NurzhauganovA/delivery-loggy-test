-- upgrade --
ALTER TABLE "item" DROP CONSTRAINT "item_itemcategory_id_fkey";
CREATE TABLE IF NOT EXISTS "categories" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "item_type" VARCHAR(8) NOT NULL,
    "value" INT NOT NULL,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "categories"."item_type" IS 'FOOD: food, COMMON: common, DOCUMENT: document';;
ALTER TABLE "item" RENAME COLUMN "itemcategory_id" TO "category_id";
ALTER TABLE "profile_courier" ADD "category_id" INT;
ALTER TABLE "profile_courier" DROP COLUMN "category";
DROP TABLE IF EXISTS "itemcategory";
ALTER TABLE "item" ADD CONSTRAINT "item_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "categories" ("id") ON DELETE SET NULL;
ALTER TABLE "profile_courier" ADD CONSTRAINT "profile_courier_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "categories" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "profile_courier" DROP CONSTRAINT "profile_courier_category_id_fkey";
ALTER TABLE "item" DROP CONSTRAINT "item_category_id_fkey";
ALTER TABLE "item" RENAME COLUMN "category_id" TO "itemcategory_id";
ALTER TABLE "profile_courier" ADD "category" VARCHAR(1) NOT NULL  DEFAULT 'D';
ALTER TABLE "profile_courier" DROP COLUMN "category_id";
DROP TABLE IF EXISTS "categories";
CREATE TABLE IF NOT EXISTS "itemcategory" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "item_type" VARCHAR(8) NOT NULL,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE
);
ALTER TABLE "item" ADD CONSTRAINT "item_itemcategory_id_fkey" FOREIGN KEY ("itemcategory_id") REFERENCES "itemcategory" ("id") ON DELETE SET NULL;
