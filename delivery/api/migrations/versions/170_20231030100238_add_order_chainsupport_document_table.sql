-- upgrade --
CREATE TABLE IF NOT EXISTS "order_chain_stage_supporting_document" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "document_number" VARCHAR(255) NOT NULL,
    "image" TEXT NOT NULL,
    "comment" TEXT,
    "order_chain_stage_id" INT NOT NULL REFERENCES "order_chain_stage" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "order_chain_stage_supporting_document";
