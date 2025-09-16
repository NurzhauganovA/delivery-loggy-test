-- upgrade --
UPDATE "order" SET "deliverygraph_id" = "subquery"."deliverygraph_id" FROM (
    SELECT "id", "deliverygraph_id" FROM "item"
                                    ) AS "subquery" WHERE "order".item_id = "subquery".id;
-- downgrade --
UPDATE "order" SET "deliverygraph_id" = 1 WHERE TRUE;