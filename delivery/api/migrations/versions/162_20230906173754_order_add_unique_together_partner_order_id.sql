-- upgrade --
CREATE UNIQUE INDEX "uid_order_partner_1dce66" ON "order" ("partner_order_id", "partner_id") WHERE "partner_id" IS NOT NULL AND "partner_order_id" IS NOT NULL;
-- downgrade --
ALTER TABLE "order" DROP CONSTRAINT "uid_order_partner_1dce66";
