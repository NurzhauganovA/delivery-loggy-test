from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from tortoise import Model, fields
from tortoise.timezone import now

from api import models
from api.context_vars import locale_context


class City(Model):
    id = fields.IntField(pk=True)
    name_en = fields.CharField(max_length=255, null=True)
    name_kk = fields.CharField(max_length=255, null=True)
    name_ru = fields.CharField(max_length=255, null=True)
    name_zh = fields.CharField(max_length=255, null=True)
    country: fields.ForeignKeyRelation[
        'models.Country'
    ] = fields.ForeignKeyField(
        'versions.Country',
        'cities',
        fields.RESTRICT,
    )
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    timezone = fields.CharField(50, null=True)

    # type hints
    item_set: fields.ManyToManyRelation['models.Item']
    country_id: int | None

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'city'
        unique_together = ('name', 'country')

    @property
    def name(self):
        locale = locale_context.get()
        return getattr(self, f'name_{locale}', self.name_en)

    def __str__(self):
        return f'{self.id} - {self.name}'

    @property
    def tz(self):
        try:
            return ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError:
            pass
        return ZoneInfo('UTC')

    @property
    def localtime(self) -> datetime:
        current_time = now()
        return current_time + self.tz.utcoffset(current_time)
