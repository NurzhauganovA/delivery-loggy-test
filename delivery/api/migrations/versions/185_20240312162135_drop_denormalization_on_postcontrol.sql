-- upgrade --
ALTER TABLE "order.postcontrols" DROP COLUMN "document_code";
ALTER TABLE "order.postcontrols" DROP COLUMN "send";
-- downgrade --
ALTER TABLE "order.postcontrols" ADD "document_code" VARCHAR(255);
ALTER TABLE "order.postcontrols" ADD "send" BOOL NOT NULL  DEFAULT False;
