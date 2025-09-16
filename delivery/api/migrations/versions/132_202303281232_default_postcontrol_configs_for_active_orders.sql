-- upgrade --
-- copy default postcontrol configs to active orders from items.
UPDATE "order"
SET "postcontrol_configs"="item"."postcontrol_configs"
FROM (SELECT "i"."id", -- getting postcontrol config objects
             json_agg(
                     json_build_object(
                             'id', pc.id,
                             'name', pc.name,
                             'inner_params', pc.inner_params
                         )
                 ) "postcontrol_configs"
      FROM "item" "i"
               LEFT OUTER JOIN (SELECT "p"."item_id",  --- getting inner params
                                       p."id",
                                       p."name",
                                       CASE
                                           WHEN COUNT("in"."id") = 0 THEN '[]'
                                           ELSE
                                               json_agg(
                                                       json_build_object('id', "in"."id", 'name', "in"."name")
                                                   )
                                           END inner_params
                                FROM "postcontrol_configs" "p"
                                         LEFT OUTER JOIN "postcontrol_configs" "in" on "in".parent_config_id = "p"."id"
                                GROUP BY "p"."id", "p"."name", "p"."item_id") "pc"
                               on "i"."id" = "pc"."item_id"
      WHERE pc.id IS NOT NULL
      GROUP BY "i"."id") "item"
WHERE "item"."id" = "order"."item_id"
  AND "order"."postcontrol_configs" = '[]'
  AND NOT EXISTS (SELECT id from "order.statuses" WHERE order_id="order".id and "status_id" in (7, 27)); -- condition to get only active orders
-- downgrade --
SELECT *
FROM "order"
LIMIT 1;
