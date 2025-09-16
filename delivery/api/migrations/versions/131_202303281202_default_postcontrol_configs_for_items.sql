-- upgrade --
-- populate existing items with default postcontrol configs
INSERT INTO "postcontrol_configs" ("item_id", "name", "send")
SELECT "id"           AS "item_id",
       'фото клиента' AS "name",
       true           AS "send"
FROM "item"
WHERE
  "has_postcontrol" IS TRUE                         -- this condition set literally says:
  AND "id" NOT IN (SELECT "item_id"                 -- select all items which subject to postcontrol
                   FROM "postcontrol_configs"       -- but has no postcontrol configs.
                   WHERE "item_id" IS NOT NULL      --
                   GROUP BY "item_id");             --
-- downgrade --
SELECT *
FROM "postcontrol_configs"
LIMIT 1;
