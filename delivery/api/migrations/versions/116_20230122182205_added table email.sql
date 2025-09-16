-- upgrade --
CREATE TABLE IF NOT EXISTS "email" (
    "mail" VARCHAR(100) NOT NULL  PRIMARY KEY
);
-- downgrade --
DROP TABLE IF EXISTS "email";