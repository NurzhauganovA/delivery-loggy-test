from pydantic import BaseModel, root_validator

from ..enums import PostControlType
from ..enums import PostControlResolution


class PostControlBase(BaseModel):
    id: int
    order_id: int
    image: str | None
    config_id: int | None

    class Config:
        extra = 'ignore'


class PostControl(PostControlBase):
    resolution: str | None
    comment: str | None


class PostControlGet(PostControl):
    type: PostControlType

    class Config:
        use_enum_values = True
        orm_mode = True


class PostControlMakeResolution(BaseModel):
    id: int
    resolution: PostControlResolution
    comment: str | None

    class Config:
        use_enum_values = True

    # noinspection PyMethodParameters
    @root_validator()
    def check_comment(cls, values):
        resolution = values.get('resolution')
        comment = values.get('comment')
        if resolution in (PostControlResolution.DECLINED, PostControlResolution.BANK_DECLINED):
            if not comment:
                raise ValueError('Comment field is required if post control was declined')
            if len(comment) < 5:
                raise ValueError('Comment must contain at least 5 characters')
        else:
            values['comment'] = None
        return values
