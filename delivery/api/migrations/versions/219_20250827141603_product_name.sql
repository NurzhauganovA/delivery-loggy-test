-- upgrade --
ALTER TABLE public.product ADD IF NOT EXISTS "name" VARCHAR(100);
-- downgrade --
ALTER TABLE public.product DROP COLUMN IF EXISTS "name";
