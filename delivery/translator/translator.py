import json
from aiofiles import os
from aiofiles import open
from typing import Any, Dict

from ._helpers import get_package_root


class Translator:
    _instances: Dict[str, 'Translator'] = {}

    def __new__(cls, locale: str, **args: Any) -> 'Translator':
        if locale not in cls._instances:
            cls._instances[locale] = super().__new__(cls)
        return cls._instances[locale]

    def __init__(self, locale: str, locale_path: str):
        self.locale = locale
        self.locale_path = locale_path.rstrip('/')
        self.translations: Dict[str, Any] = {}

    async def load_translation(self, file_key: str = 'message') -> Any | Dict[str, Any] | None:
        if file_key in self.translations:
            return self.translations[file_key]
        file_path = f'{self.locale_path}/{self.locale}/{file_key}.json'
        if not await os.path.isfile(file_path):
            file_path = str(
                (await get_package_root()).joinpath(f'locales/{self.locale}/{file_key}.json'))
        try:
            async with open(file_path, encoding='utf-8', mode='r') as file:
                translation = json.loads(await file.read())
            self.translations[file_key] = translation
            return translation
        except FileNotFoundError:
            return None

    async def t(self, key: str, **kwargs: Any) -> str:
        translation_dict = await self.load_translation()
        if translation_dict is None:
            return key

        translation = translation_dict.get(key, key)

        if kwargs:
            translated_kwargs = {}
            for k, v in kwargs.items():
                translated_kwargs[k] = translation_dict.get(v, v)
            translation = translation.format(**translated_kwargs)  # type: ignore

        return translation


__all__ = ['Translator']
