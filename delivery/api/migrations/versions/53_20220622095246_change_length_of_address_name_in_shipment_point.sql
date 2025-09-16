-- upgrade --
ALTER TABLE "partner.shipment_points" ALTER COLUMN "name" TYPE VARCHAR(200) USING "name"::VARCHAR(200);
-- downgrade --
ALTER TABLE "partner.shipment_points" ALTER COLUMN "name" TYPE VARCHAR(50) USING "name"::VARCHAR(50);
