-- upgrade --
INSERT INTO public.status (id, icon, name, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code)
VALUES (
        37,
        'transfer_to_cdek',
        'Передано в СДЭК',
        false,
        null,
        null,
        'peredano-v-cdek',
        'Transfer to CDEK',
        null,
        'Передано в СДЭК',
        'Передано в СДЭК',
        'transfer_to_cdek'
);
UPDATE status
SET code = 'scan_card'
WHERE id = 24;
-- downgrade --
DELETE FROM public.status WHERE code = 'transfer_to_cdek';
UPDATE status
SET code = null
WHERE id = 24;
