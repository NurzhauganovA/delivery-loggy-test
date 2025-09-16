-- upgrade --
INSERT INTO "public"."product"
("created_at", "type", "attributes", "pan_suffix", "order_id")
SELECT "created_at", 'card', json_build_object('pan', "pan", 'pan_suffix', RIGHT("pan", 4)), RIGHT("pan", 4), "order_id" FROM "order_pan" ORDER BY "created_at" DESC
ON CONFLICT DO NOTHING;
-- downgrade --
SELECT 1;