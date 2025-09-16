-- upgrade --
INSERT INTO public.status (id, icon, name, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code)
VALUES (36, 'pos_terminal_registration', 'Ввод серийного номера и модели', false, null, null, 'pos-terminal-registration', 'Enter serial number and model', null, 'Ввод серийного номера и модели', 'Ввод серийного номера и модели', 'pos_terminal_registration');
-- downgrade --
DELETE FROM public.status WHERE code = 'pos_terminal_registration'
