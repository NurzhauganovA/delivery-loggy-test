-- upgrade --
ALTER TABLE "order.postcontrols" ALTER COLUMN "resolution" TYPE VARCHAR(13) USING "resolution"::VARCHAR(13);
-- downgrade --
ALTER TABLE "order.postcontrols" ALTER COLUMN "resolution" TYPE VARCHAR(8) USING "resolution"::VARCHAR(8);
