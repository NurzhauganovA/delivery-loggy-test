import datetime
from typing import Optional

import pydantic
from pydantic import BaseModel


class ReportFilter(BaseModel):
    city_id__in: Optional[pydantic.conlist(int, min_items=1)]
    partner_id__in: Optional[pydantic.conlist(int, min_items=1)]
    courier_id__in: Optional[pydantic.conlist(int, min_items=1)]
    current_status__in: Optional[pydantic.conlist(int, min_items=1)]
    address_set__place_id__in: Optional[pydantic.conlist(int, min_items=1)]
    created_at__range: Optional[pydantic.conlist(datetime.datetime, min_items=2, max_items=2)]
    fact_delivery_time__range: Optional[pydantic.conlist(datetime.datetime, min_items=2, max_items=2)]
    were_in_status: Optional[pydantic.conlist(int, min_items=1)]
    current_status__created_at__range: Optional[pydantic.conlist(datetime.datetime, min_items=2, max_items=2)]


class ExportExcel(BaseModel):
    """
    Schema for the export excel endpoint
    """
    filtering: ReportFilter
    # ordering: typing.List[enums.OrderReportOrdering]

    # class Config:
    #     use_enum_values = True
