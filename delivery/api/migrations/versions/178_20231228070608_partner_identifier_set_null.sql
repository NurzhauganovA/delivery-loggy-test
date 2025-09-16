-- upgrade --
ALTER TABLE "partner" ALTER COLUMN "identifier" DROP NOT NULL;
-- downgrade --
ALTER TABLE "partner" ALTER COLUMN "identifier" TYPE varchar(12) USING (COALESCE("identifier", ''));
ALTER TABLE "partner" ALTER COLUMN "identifier" SET NOT NULL;
