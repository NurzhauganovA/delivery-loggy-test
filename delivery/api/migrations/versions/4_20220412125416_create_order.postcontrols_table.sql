-- upgrade --
CREATE TABLE IF NOT EXISTS "order.postcontrols" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "image" TEXT NOT NULL,
    "resolution" VARCHAR(8),
    "comment" TEXT,
    "order_id" INT NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "order.postcontrols"."resolution" IS 'ACCEPTED: accepted, DECLINED: declined';
-- downgrade --
DROP TABLE IF EXISTS "order.postcontrols";
