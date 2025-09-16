-- upgrade --
ALTER TABLE "order" ADD "order_group_id" INT;
ALTER TABLE "order" ADD CONSTRAINT "fk_order_order_gr_15e2d314" FOREIGN KEY ("order_group_id") REFERENCES "order_group" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "order" DROP CONSTRAINT "fk_order_order_gr_15e2d314";
ALTER TABLE "order" DROP COLUMN "order_group_id";
