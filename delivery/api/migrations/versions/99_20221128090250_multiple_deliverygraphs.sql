-- upgrade --
CREATE TABLE "item_deliverygraph" ("deliverygraph_id" INT NOT NULL REFERENCES "deliverygraph" ("id") ON DELETE CASCADE,"item_id" INT NOT NULL REFERENCES "item" ("id") ON DELETE CASCADE);
INSERT INTO "item_deliverygraph" (item_id, deliverygraph_id) SELECT "id" as "item_id", "deliverygraph_id" FROM "item";
ALTER TABLE "item" DROP CONSTRAINT "item_deliverygraph_id_fkey";
ALTER TABLE "deliverygraph" ADD "types" varchar[] NOT NULL DEFAULT array['urgent', 'operative', 'planned']::varchar[];
ALTER TABLE "item" DROP COLUMN "deliverygraph_id";
ALTER TABLE "order" ALTER COLUMN "type" TYPE VARCHAR(9) USING "type"::VARCHAR(9);
-- downgrade --
DROP TABLE IF EXISTS "item_deliverygraph";
ALTER TABLE "item" ADD "deliverygraph_id" INT;
ALTER TABLE "order" ALTER COLUMN "type" TYPE VARCHAR(9) USING "type"::VARCHAR(9);
ALTER TABLE "deliverygraph" DROP COLUMN "types";
ALTER TABLE "item" ADD CONSTRAINT "item_deliverygraph_id_fkey" FOREIGN KEY ("deliverygraph_id") REFERENCES "deliverygraph" ("id") ON DELETE SET NULL;
