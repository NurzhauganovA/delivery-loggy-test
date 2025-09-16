import os
from typing import Optional

import tortoise
from loguru import logger
from tortoise import BaseDBAsyncClient

from ..conf import conf
from . import fields as custom_fields


fields = tortoise.fields


class DeleteFilesMixin:
    async def delete(
        self, using_db: Optional[BaseDBAsyncClient] = None,
    ) -> None:
        await super().delete(using_db)
        for image in self.file_fields:
            try:
                if file_path := getattr(self, image):
                    os.remove(conf.media.root / file_path.replace(conf.media.url + '/', ''))
            except OSError as e:
                logger.error(str(e))

    @property
    def file_fields(self):
        return [name for name, field in self._meta.fields_map.items() if
                isinstance(field, custom_fields.FileField)]
