-- upgrade --
ALTER TABLE "order" ADD "allow_courier_assign" BOOL NOT NULL  DEFAULT True;
-- downgrade --
ALTER TABLE "order" DROP COLUMN "allow_courier_assign";
