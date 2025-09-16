-- upgrade --
ALTER TABLE "order" ALTER COLUMN "receiver_name" DROP NOT NULL;
-- downgrade --
ALTER TABLE "order" ALTER COLUMN "receiver_name" TYPE varchar(255) USING (COALESCE("receiver_name", ''));
ALTER TABLE "order" ALTER COLUMN "receiver_name" SET NOT NULL;
