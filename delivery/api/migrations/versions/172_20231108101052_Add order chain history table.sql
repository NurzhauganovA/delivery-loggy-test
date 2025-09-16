-- upgrade --
CREATE TABLE IF NOT EXISTS "order_chain_history" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "initiator_id" INT,
    "initiator_type" VARCHAR(15) NOT NULL  DEFAULT 'User',
    "request_method" VARCHAR(7) NOT NULL,
    "model_type" VARCHAR(50) NOT NULL,
    "action_data" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "initiator_role" VARCHAR(22),
    "model_id" INT NOT NULL REFERENCES "order_chain" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "order_chain_history"."initiator_type" IS 'IMPORT: Import, USER: User, EXTERNAL_SERVICE: ExternalService';
COMMENT ON COLUMN "order_chain_history"."request_method" IS 'GET: GET, POST: POST, PUT: PUT, DELETE: DELETE, PATCH: PATCH, HEAD: HEAD, OPTIONS: OPTIONS';
COMMENT ON COLUMN "order_chain_history"."initiator_role" IS 'COURIER: courier, DISPATCHER: dispatcher, MANAGER: manager, OWNER: owner, SERVICE_MANAGER: service_manager, BRANCH_MANAGER: branch_manager, PARTNER_BRANCH_MANAGER: partner_branch_manager, SORTER: sorter';
-- downgrade --
DROP TABLE IF EXISTS "order_chain_history";
