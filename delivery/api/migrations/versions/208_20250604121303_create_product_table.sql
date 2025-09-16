-- upgrade --
CREATE TABLE IF NOT EXISTS "product" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "type" VARCHAR(20) NOT NULL,
    "attributes" JSONB NOT NULL,
    "pan_suffix" VARCHAR(4),
    "order_id" INT NOT NULL UNIQUE REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_product_pan_suf_95cf48" ON "product" ("pan_suffix");;
-- downgrade --
DROP TABLE IF EXISTS "product";
