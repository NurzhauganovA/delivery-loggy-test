-- upgrade --
ALTER TABLE "order" ADD "main_order_id_id" INT;
ALTER TABLE "order" ADD CONSTRAINT "fk_order_order_b8bc033a" FOREIGN KEY ("main_order_id_id") REFERENCES "order" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "order" DROP CONSTRAINT "fk_order_order_b8bc033a";
ALTER TABLE "order" DROP COLUMN "main_order_id_id";
