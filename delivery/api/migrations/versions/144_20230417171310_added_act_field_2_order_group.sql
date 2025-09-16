-- upgrade --
ALTER TABLE "order_group" ADD "act" TEXT;
-- downgrade --
ALTER TABLE "order_group" DROP COLUMN "act";
