-- upgrade --
ALTER TABLE "feedback" ALTER COLUMN "author_phone" TYPE VARCHAR(13) USING "author_phone"::VARCHAR(13);
ALTER TABLE "order" ALTER COLUMN "receiver_phone_number" TYPE VARCHAR(13) USING "receiver_phone_number"::VARCHAR(13);
ALTER TABLE "invited_user" ALTER COLUMN "phone_number" TYPE VARCHAR(13) USING "phone_number"::VARCHAR(13);
-- downgrade --
ALTER TABLE "feedback" ALTER COLUMN "author_phone" TYPE VARCHAR(12) USING "author_phone"::VARCHAR(12);
ALTER TABLE "order" ALTER COLUMN "receiver_phone_number" TYPE VARCHAR(12) USING "receiver_phone_number"::VARCHAR(12);
ALTER TABLE "invited_user" ALTER COLUMN "phone_number" TYPE VARCHAR(12) USING "phone_number"::VARCHAR(12);
