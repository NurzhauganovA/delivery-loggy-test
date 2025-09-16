import pydantic

from api.common.schema_base import BaseInSchema


class CreateCommentRequest(BaseInSchema):
    text: pydantic.constr(min_length=5, max_length=2500)
