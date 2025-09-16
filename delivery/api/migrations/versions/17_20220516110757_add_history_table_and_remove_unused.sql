-- upgrade --
CREATE TABLE IF NOT EXISTS "history" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "request_method" VARCHAR(7) NOT NULL,
    "model_type" VARCHAR(50) NOT NULL,
    "action_data" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "initiator_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "history"."request_method" IS 'GET: GET, POST: POST, PUT: PUT, DELETE: DELETE, PATCH: PATCH, HEAD: HEAD, OPTIONS: OPTIONS';;
ALTER TABLE "partner.addresses" RENAME TO "partner.shipment_points";
DROP TABLE IF EXISTS "partner.addresses";
DROP TABLE IF EXISTS "partner_history";
DROP TABLE IF EXISTS "useractionlogs";
-- downgrade --
DROP TABLE IF EXISTS "history";
ALTER TABLE "partner.shipment_points" RENAME TO "partner.addresses";
