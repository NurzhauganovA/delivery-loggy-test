-- upgrade --
ALTER TABLE "order.postcontrols" RENAME COLUMN "code" TO "document_code";
ALTER TABLE "postcontrol_configs" RENAME COLUMN "code" TO "document_code";
-- downgrade --
ALTER TABLE "order.postcontrols" RENAME COLUMN "document_code" TO "code";
ALTER TABLE "postcontrol_configs" RENAME COLUMN "document_code" TO "code";
