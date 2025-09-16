from typing import Optional, Any, Iterator

import pydantic
from pydantic import BaseModel


class ImportExcelResponse(BaseModel):
    file: Any
    result: Optional[pydantic.constr()]
