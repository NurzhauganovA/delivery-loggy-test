-- upgrade --
ALTER TABLE "order" ADD "current_status_id" INT;
ALTER TABLE "order" ADD CONSTRAINT "fk_order_status_7577cd64" FOREIGN KEY ("current_status_id") REFERENCES "status" ("id") ON DELETE SET NULL;
UPDATE "order" SET "current_status_id" = (SELECT "status_id" FROM "order.statuses" WHERE "order_id" = "order"."id" ORDER BY "created_at" DESC LIMIT 1);

-- downgrade --
ALTER TABLE "order" DROP CONSTRAINT "fk_order_status_7577cd64";
ALTER TABLE "order" DROP COLUMN "current_status_id";
