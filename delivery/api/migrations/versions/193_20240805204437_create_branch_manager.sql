-- upgrade --
ALTER TABLE "history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
CREATE TABLE IF NOT EXISTS "profile_bank_manager" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL UNIQUE REFERENCES "user" ("id") ON DELETE CASCADE
);;
ALTER TABLE "order_chain_history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
ALTER TABLE "partner_shipment_point_history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
-- downgrade --
ALTER TABLE "history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
ALTER TABLE "order_chain_history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
ALTER TABLE "partner_shipment_point_history" ALTER COLUMN "initiator_role" TYPE VARCHAR(22) USING "initiator_role"::VARCHAR(22);
DROP TABLE IF EXISTS "profile_bank_manager";
