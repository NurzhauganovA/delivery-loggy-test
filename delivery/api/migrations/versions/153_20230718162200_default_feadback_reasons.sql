-- upgrade --
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Курьер был груб' "name", "p"."id" "partner_id", true "is_tag", '{"0": -20}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Курьер проявил агрессию' "name", "p"."id" "partner_id", true "is_tag", '{"0": -30}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Курьер использовал ненормативную лексиску' "name", "p"."id" "partner_id", true "is_tag", '{"1": -10}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Курьер проявил вежливость' "name", "p"."id" "partner_id", true "is_tag", '{"5": 20}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Курьер был очень вежлив и учтив' "name", "p"."id" "partner_id", true "is_tag", '{"5": 25}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Все прошло хорошо' "name", "p"."id" "partner_id", true "is_tag", '{"5": 15}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Все прошло отлично' "name", "p"."id" "partner_id", true "is_tag", '{"5": 20}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Все прошло нормально' "name", "p"."id" "partner_id", true "is_tag", '{"5": 10}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;
INSERT INTO "feedback_reason"
    ("name", "partner_id", "is_tag", "value")
SELECT 'Ничего необычного' "name", "p"."id" "partner_id", true "is_tag", '{"4": 0}' "value"
FROM "partner" "p"
WHERE "courier_partner_id" is null;

-- downgrade --
SELECT 'dummy migration';