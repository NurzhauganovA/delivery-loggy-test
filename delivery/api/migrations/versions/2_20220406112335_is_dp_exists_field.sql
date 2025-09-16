-- upgrade --
ALTER TABLE "item" ADD "is_delivery_point_exists" BOOL NOT NULL  DEFAULT True;
-- downgrade --
ALTER TABLE "item" DROP COLUMN "is_delivery_point_exists";
