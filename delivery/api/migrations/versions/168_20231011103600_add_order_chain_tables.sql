-- upgrade --
CREATE TABLE IF NOT EXISTS "order_chain_receiver" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "phone_number" VARCHAR(255) NOT NULL,
    "email" VARCHAR(100),
    "address" VARCHAR(255) NOT NULL,
    "latitude" DECIMAL(10,8),
    "longitude" DECIMAL(11,8),
    "city_id" INT REFERENCES "city" ("id") ON DELETE SET NULL
);;
CREATE TABLE IF NOT EXISTS "order_chain_sender" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "phone_number" VARCHAR(255) NOT NULL,
    "email" VARCHAR(100),
    "address" VARCHAR(255) NOT NULL,
    "latitude" DECIMAL(10,8),
    "longitude" DECIMAL(11,8),
    "city_id" INT REFERENCES "city" ("id") ON DELETE SET NULL
);;
CREATE TABLE IF NOT EXISTS "order_chain" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "external_id" VARCHAR(255),
    "comment" VARCHAR(255),
    "package_params" JSONB,
    "type" VARCHAR(7) NOT NULL  DEFAULT 'simple',
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fact_delivery_datetime" TIMESTAMPTZ,
    "expected_delivery_datetime" TIMESTAMPTZ,
    "deadline_delivery_datetime" TIMESTAMPTZ,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE,
    "receiver_id" INT NOT NULL REFERENCES "order_chain_receiver" ("id") ON DELETE CASCADE,
    "sender_id" INT NOT NULL REFERENCES "order_chain_sender" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "order_chain"."type" IS 'SIMPLE: simple, EXPRESS: express';;
CREATE TABLE IF NOT EXISTS "order_chain_stage" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "type" VARCHAR(4) NOT NULL  DEFAULT 'road',
    "position" INT NOT NULL,
    "order_id" INT NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE,
    "order_chain_id" INT NOT NULL REFERENCES "order_chain" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "order_chain_stage"."type" IS 'AIR: air, SEA: sea, RAIL: rail, ROAD: road';-- downgrade --
DROP TABLE IF EXISTS "order_chain";
DROP TABLE IF EXISTS "order_chain_receiver";
DROP TABLE IF EXISTS "order_chain_sender";
DROP TABLE IF EXISTS "order_chain_stage";
