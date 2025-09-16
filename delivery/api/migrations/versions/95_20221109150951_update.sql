-- upgrade --
ALTER TABLE "order" ADD "deliverygraph_id" INT NOT NULL DEFAULT 1;
ALTER TABLE "order" ADD CONSTRAINT "order_deliverygraph_id_fkey" FOREIGN KEY ("deliverygraph_id") REFERENCES "deliverygraph" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "order" DROP CONSTRAINT "order_deliverygraph_id_fkey";
ALTER TABLE "order" DROP COLUMN "deliverygraph_id";
