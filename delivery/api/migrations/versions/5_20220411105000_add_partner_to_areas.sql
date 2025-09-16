-- upgrade --
ALTER TABLE "area" ADD "partner_id" INT NOT NULL;
ALTER TABLE "area" ADD CONSTRAINT "fk_area_partner_690087d4" FOREIGN KEY ("partner_id") REFERENCES "partner" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "area" DROP CONSTRAINT "fk_area_partner_690087d4";
ALTER TABLE "area" DROP COLUMN "partner_id";
