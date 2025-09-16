from pydantic import BaseModel
from pydantic import main


class BaseInSchema(BaseModel):
    pass


class BaseOutSchema(BaseModel):
    class Config(BaseModel.Config):
        orm_mode = True


class BaseFilterSchema(BaseModel):
    pass


class AllOptional(main.ModelMetaclass):
    def __new__(mcs, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
            ancestors = base.mro()
            for ancestor in ancestors:
                if hasattr(ancestor, '__annotations__'):
                    annotations.update(ancestor.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = annotations[field] | None
        namespaces['__annotations__'] = annotations
        return super().__new__(mcs, name, bases, namespaces, **kwargs)


def partial(cls):
    """
    Class factory that generates pydantic model for partial update requests.
    usage: partial(<pydantic Model>)
    explanation:
        consider:
        class ItemUpdate(BaseModel):
            name: str
            count: int
    then:
    ItemPartialUpdate = partial(ItemUpdate)
    is equivalent to:
    class ItemPartialUpdate(BaseModel):
        name: Optional[str]
        count: Optional[int]

    Note: the name of newly generated model will derive
    from the model which was given as an argument.
    """
    name = cls.__name__.replace('Update', 'PartialUpdate')
    partial_class = AllOptional(name, (cls,), {})
    return partial_class


__all__ = (
    'BaseFilterSchema',
    'BaseInSchema',
    'BaseOutSchema',
    'partial',
)
