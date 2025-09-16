-- upgrade --
UPDATE public.status
SET slug = 'vvod-seriynogo-nomera-i-modeli'
WHERE public.status.id = 36;
-- downgrade --
UPDATE public.status
SET slug = 'pos_terminal_registration'
WHERE public.status.id = 36;