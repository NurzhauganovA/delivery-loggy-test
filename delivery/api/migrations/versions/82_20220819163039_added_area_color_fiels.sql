-- upgrade --
ALTER TABLE "area" ADD "fill_opacity" DOUBLE PRECISION NOT NULL DEFAULT 0.6;
ALTER TABLE "area" ADD "stroke_color" VARCHAR(15) NOT NULL DEFAULT '#ff0000';
ALTER TABLE "area" ADD "stroke_opacity" DOUBLE PRECISION NOT NULL DEFAULT 1.0;
ALTER TABLE "area" ADD "fill_color" VARCHAR(15) NOT NULL DEFAULT '#ff0000';
-- downgrade --
ALTER TABLE "area" DROP COLUMN "fill_opacity";
ALTER TABLE "area" DROP COLUMN "stroke_color";
ALTER TABLE "area" DROP COLUMN "stroke_opacity";
ALTER TABLE "area" DROP COLUMN "fill_color";
