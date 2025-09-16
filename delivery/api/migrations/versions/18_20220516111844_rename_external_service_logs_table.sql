-- upgrade --
ALTER TABLE "external_service_logs" RENAME TO "external_service_history";
-- downgrade --
ALTER TABLE "external_service_history" RENAME TO "external_service_logs";
