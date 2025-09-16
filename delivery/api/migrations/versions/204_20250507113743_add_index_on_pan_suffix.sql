-- upgrade --
CREATE INDEX "order_pan_pan_suffix_idx" ON "order_pan" ("pan_suffix");
-- downgrade --
DROP INDEX "order_pan_pan_suffix_idx";
