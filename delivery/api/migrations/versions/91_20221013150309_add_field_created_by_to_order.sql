-- upgrade --
ALTER TABLE "order" ADD "created_by" VARCHAR(11) NOT NULL  DEFAULT 'service';
-- downgrade --
ALTER TABLE "order" DROP COLUMN "created_by";
