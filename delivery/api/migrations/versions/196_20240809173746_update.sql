-- upgrade --
ALTER TABLE "deliverygraph" ADD "graph_courier" JSONB NOT NULL DEFAULT '[]'::JSONB;
UPDATE "deliverygraph" SET "graph_courier"="graph" WHERE TRUE;
-- downgrade --
ALTER TABLE "deliverygraph" DROP COLUMN "graph_courier";
