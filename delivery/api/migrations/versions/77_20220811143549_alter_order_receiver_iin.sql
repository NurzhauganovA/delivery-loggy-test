-- upgrade --
ALTER TABLE "order" ALTER COLUMN "receiver_iin" DROP NOT NULL;
-- downgrade --
ALTER TABLE "order" ALTER COLUMN "receiver_iin" SET NOT NULL;
