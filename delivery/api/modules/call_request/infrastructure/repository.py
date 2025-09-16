from typing import List
from typing import Tuple
from typing import Type

from api.common.repository_base import BaseRepository, TABLE, SCHEMA
from .db_table import *
from ..errors import *
from ..schemas import *


class CallRequestRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return CallRequestOut

    @property
    def _table(self) -> Type[TABLE]:
        return CallRequest

    @property
    def _not_found_error(self) -> Type[CallRequestNotFoundError]:
        return CallRequestNotFoundError

    @property
    def _integrity_error(self) -> Type[CallRequestIntegrityError]:
        return CallRequestIntegrityError


class CallRequestContactRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return CallRequestOut

    @property
    def _table(self) -> Type[TABLE]:
        return CallRequestContact

    @property
    def _not_found_error(self) -> Type[CallRequestContactNotFoundError]:
        return CallRequestContactNotFoundError

    @property
    def _integrity_error(self) -> Type[CallRequestContactIntegrityError]:
        return CallRequestContactIntegrityError

    async def get_contacts(self) -> List[Tuple[str]]:
        return await self._table.all().values_list('phone', 'email')


__all__ = (
    'CallRequestRepository',
    'CallRequestContactRepository',
)
