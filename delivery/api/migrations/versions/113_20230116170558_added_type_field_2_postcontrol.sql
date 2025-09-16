-- upgrade --
ALTER TABLE "order.postcontrols" ADD "type" VARCHAR(18) NOT NULL  DEFAULT 'post_control';
-- downgrade --
ALTER TABLE "order.postcontrols" DROP COLUMN "type";
