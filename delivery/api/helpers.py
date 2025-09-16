import typing

from transliterate import translit
from transliterate.base import TranslitLanguagePack, registry
import random
import string


class ArticleGenerator:
    ACRONYM_LENGTH = 4

    class KazakhLanguagePack(TranslitLanguagePack):
        language_code = "kz"
        language_name = "Kazakh"

        reversed_specific_pre_processor_mapping = {
            u"Ж": u"ZH",
            u"Ш": u"SH",
            u"Щ": u"SH",
            u"Ч": u"CH",
            u"Ю": u"IU",
            u"Я": u"IA",
            u"Ц": u"TS",
            u"Қ": u"Q",
            u"Н": u"N",
        }
        mapping = (
            u"ABVGDEEZIIKLMNPORSTUFHYEAINGUUKOH",
            u"АБВГДЕЁЗИЙКЛМНПОРСТУФХЫЭӘІҢҒҮҰҚӨҺ",
        )

    @classmethod
    def __is_unique_acronym(cls, acronym: str, acronym_list: typing.List[str]):
        if acronym not in acronym_list:
            return True

    @classmethod
    def _one_world_acronym(cls, word: str, acronym_list: typing.List[str]) -> str:
        count = 0
        while True:
            acronym = word[:cls.ACRONYM_LENGTH + count]
            acronym = translit(acronym.upper(), 'kz', reversed=True)
            if cls.__is_unique_acronym(acronym, acronym_list):
                return acronym
            count += 1


    @classmethod
    def _several_worlds_acronym(
            cls, words_list: typing.List[str], acronym_list: typing.List[str]
    ) -> str:
        count = 0
        acronym = ''
        while True:
            for s in words_list[:4]:
                if count == 0:
                    acronym += s[0]
                else:
                    acronym += s[:count]
            acronym = translit(acronym.upper(), 'kz', reversed=True)
            if cls.__is_unique_acronym(acronym, acronym_list):
                return acronym
            count += 1

    @staticmethod
    def _normalize_name(
            name, words_to_remove: typing.List[str],
    ):
        cleaned = ''.join(s for s in name if s.isalpha() or s == " ")
        words_list = cleaned.replace('  ', ' ').strip().split(' ')
        for word in words_list:
            if word in words_to_remove:
                words_list.remove(word)

        return words_list

    @classmethod
    def generate_article(cls, data, acronym_list):
        registry.register(cls.KazakhLanguagePack)
        words_to_remove = []

        if name := data.get('name_en'):
            words_to_remove = ['JIC', 'JSC']

        elif name := data.get('name_kk'):
            words_to_remove = [
                'ЖШС', 'АҚ', 'жауапкершілігі шектеулі серіктестігі',
                'республикалық мемлекеттік мекемесі',
            ]

        elif name := data.get('name_ru'):
            words_to_remove = [
                'ТОО', 'АО', 'Товарищество с ограниченной ответственностью ',
                'Республиканское государственное учреждение'
            ]
        elif name := data.get('name'):
            words_to_remove = [
                'JIC', 'JSC',
                'ЖШС', 'АҚ', 'жауапкершілігі шектеулі серіктестігі', 'республикалық мемлекеттік мекемесі',
                'ТОО', 'АО', 'Товарищество с ограниченной ответственностью ', 'Республиканское государственное учреждение'
            ]
        words_list = cls._normalize_name(name, words_to_remove)
        article = ''.join(random.sample(string.ascii_uppercase, 3))

        if len(words_list) > 1:
            article = cls._several_worlds_acronym(words_list, acronym_list)
        elif len(words_list) == 1:
            article = cls._one_world_acronym(words_list[0], acronym_list)

        return article