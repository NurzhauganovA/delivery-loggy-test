-- upgrade --
update item set delivery_type=null;
ALTER TABLE "item" ALTER COLUMN "delivery_type" TYPE varchar[] USING "delivery_type"::varchar[];
ALTER TABLE "item" ALTER COLUMN "delivery_type" SET DEFAULT null;
-- downgrade --
ALTER TABLE "item" ALTER COLUMN "delivery_type" TYPE VARCHAR(9) USING "delivery_type"::VARCHAR(9);
ALTER TABLE "item" ALTER COLUMN "delivery_type" DROP DEFAULT;


