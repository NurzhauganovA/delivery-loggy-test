from random import choice
from random import randint
from string import ascii_lowercase
from string import digits

from pypika.terms import Term, BasicCriterion
from slugify import slugify

from ..conf import conf


class In(BasicCriterion):
    def __init__(self, left, right, alias=None) -> None:
        super().__init__('IN', left, right, alias=alias)

    def get_sql(self, quote_char='"', with_alias=False, **kwargs):
        sql = "{left}{comparator}{right}".format(
            comparator=self.comparator,
            left=self.left.get_sql(quote_char=quote_char, **kwargs),
            right=self.right.get_sql(quote_char=quote_char, **kwargs),
        )

        return sql


def _postgres_json_in(left: Term, value: tuple):
    return In(left, left.wrap_constant(value))


async def random_string_generator(size=10, chars=ascii_lowercase + digits):
    return ''.join(choice(chars) for _ in range(size))


async def unique_slug_generator(instance, source_field: str = 'name', new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(getattr(instance, source_field))
    model = instance.__class__
    max_length = model._meta.fields_map['slug'].max_length
    slug = slug[:max_length]
    qs_exists = await model.filter(slug=slug).exists()

    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug[:max_length - 5], randstr=await random_string_generator(size=4))

        return await unique_slug_generator(instance, new_slug=new_slug)
    return slug


async def create_otp(length: int = 4) -> str:
    default_otp = '1' * length
    min_bound = int('1' + ('0' * (length - 1)))
    max_bound = int('9' * length)
    return default_otp if conf.api.debug else str(randint(min_bound, max_bound))
