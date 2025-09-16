-- upgrade --
ALTER TABLE "order.postcontrols" ALTER COLUMN "resolution" SET DEFAULT 'pending';
ALTER TABLE "order.postcontrols" ALTER COLUMN "resolution" TYPE VARCHAR(8) USING COALESCE("resolution"::VARCHAR(8), 'pending');
ALTER TABLE "order.postcontrols" ALTER COLUMN "resolution" SET NOT NULL;
-- downgrade --
ALTER TABLE "order.postcontrols" ALTER COLUMN "resolution" DROP NOT NULL;
ALTER TABLE "order.postcontrols" ALTER COLUMN "resolution" DROP DEFAULT;
ALTER TABLE "order.postcontrols" ALTER COLUMN "resolution" TYPE VARCHAR(8) USING "resolution"::VARCHAR(8);