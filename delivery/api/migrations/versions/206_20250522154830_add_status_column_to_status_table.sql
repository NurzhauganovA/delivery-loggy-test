-- upgrade --
INSERT INTO public.status (id, icon, name, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code)
VALUES (35, 'card_returned_to_bank', 'Карта возвращена в банк', false, null, null, 'card-returned-to-bank', 'Card was returned to bank', null, 'Карта возвращена в банк', 'Карта возвращена в банк', 'card_returned_to_bank');
-- downgrade --
DELETE FROM public.status WHERE code = 'card_returned_to_bank'
