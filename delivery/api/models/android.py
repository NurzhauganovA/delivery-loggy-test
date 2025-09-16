from tortoise import Model
from tortoise import fields


class AndroidVersion(Model):
    version = fields.CharField(max_length=255, unique=True, null=False, default='x.x.x-LOGGY')
    created_at = fields.DatetimeField(auto_now_add=True)
    force_update = fields.BooleanField(default=True)

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'android_version'

    def __str__(self):
        return f'{self.version}'


async def get_last_android_version():
    return await AndroidVersion.all().order_by('-created_at').first()
