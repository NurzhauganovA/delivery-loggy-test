-- upgrade --
CREATE TABLE IF NOT EXISTS "pan_validation_masks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "pan_mask" VARCHAR(16) NOT NULL,
    "partner_id" INT NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_pan_validat_partner_582d3e" UNIQUE ("partner_id", "pan_mask")
);
-- downgrade --
DROP TABLE IF EXISTS "pan_validation_masks";
