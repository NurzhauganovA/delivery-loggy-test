from __future__ import annotations
from math import ceil
from typing import TypeVar, Generic, Sequence

from fastapi import Query
from fastapi_pagination.bases import AbstractParams, AbstractPage
from fastapi_pagination.bases import RawParams
from pydantic import BaseModel, parse_obj_as

T = TypeVar("T")


class Params(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    page_limit: int = Query(50, ge=1, le=500, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.page_limit,
            offset=self.page_limit * (self.page - 1),
        )


class Page(AbstractPage[T], Generic[T]):
    items: Sequence[T]
    current_page: int
    total_pages: int
    total: int

    __params_type__ = Params

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        params: Params,
        **kwargs
    ) -> Page[T]:
        total = kwargs.get('total')
        total_pages = ceil(total / params.page_limit)

        if items and not isinstance(items[0], dict):
            items = parse_obj_as(cls.__annotations__['items'], items)

        return cls(
            items=items,
            current_page=params.page,
            total_pages=total_pages,
            total=total,
        )
