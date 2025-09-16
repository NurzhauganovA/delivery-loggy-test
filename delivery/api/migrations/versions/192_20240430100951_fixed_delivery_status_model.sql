-- upgrade --
UPDATE "order" SET "delivery_status"="delivery_status" || '{"status": null}'::JSONB WHERE "delivery_status"->'status' is null;
UPDATE "order" SET "delivery_status"="delivery_status" || '{"reason": null}'::JSONB where "delivery_status"->'reason' is null;
UPDATE "order" SET "delivery_status"="delivery_status" || '{"comment": null}'::JSONB where "delivery_status"->'comment' is null;
UPDATE "order" SET "delivery_status"="delivery_status" || '{"datetime": null}'::JSONB where "delivery_status"->'datetime' is null;
ALTER TABLE "order" ALTER COLUMN "delivery_status" SET DEFAULT '{"status": null, "reason": null, "comment": null, "datetime": null}'::JSONB;
-- downgrade --
ALTER TABLE "order" ALTER COLUMN "delivery_status" SET DEFAULT '{}'::JSONB;
