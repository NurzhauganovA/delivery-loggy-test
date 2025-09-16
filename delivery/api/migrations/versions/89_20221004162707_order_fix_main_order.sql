-- upgrade --
ALTER TABLE "order" DROP CONSTRAINT "fk_order_order_b8bc033a";
ALTER TABLE "order" RENAME COLUMN "main_order_id_id" TO "main_order_id";
ALTER TABLE "order" ADD CONSTRAINT "fk_order_order_9c1fc0ce" FOREIGN KEY ("main_order_id") REFERENCES "order" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "order" DROP CONSTRAINT "fk_order_order_9c1fc0ce";
ALTER TABLE "order" RENAME COLUMN "main_order_id" TO "main_order_id_id";
ALTER TABLE "order" ADD CONSTRAINT "fk_order_order_b8bc033a" FOREIGN KEY ("main_order_id_id") REFERENCES "order" ("id") ON DELETE CASCADE;
