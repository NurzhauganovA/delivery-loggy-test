-- upgrade --
UPDATE public.status
SET code = 'new'
WHERE slug = 'novaia-zaiavka';
-- downgrade --
UPDATE public.status
SET code = null
WHERE slug = 'novaia-zaiavka';
