-- upgrade --
ALTER TABLE "order_pan" ALTER COLUMN "pan" TYPE VARCHAR(20) USING "pan"::VARCHAR(20);
-- downgrade --
ALTER TABLE "order_pan" ALTER COLUMN "pan" TYPE INT USING "pan"::INT;
