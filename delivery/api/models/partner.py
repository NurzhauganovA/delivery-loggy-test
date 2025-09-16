import typing

import tortoise
from tortoise.query_utils import Prefetch
from tortoise.queryset import Q
import tortoise.transactions
from tortoise.transactions import atomic

from api.context_vars import locale_context
from .. import verification

from .. import helpers
from .. import enums
from .. import exceptions
from .. import models
from .. import schemas
from .. import utils

from tortoise import fields

from ..modules.city.infrastructure.db_table import City
from ..modules.partner_settings import PartnerSetting
from ..modules.shipment_point import PartnerShipmentPoint
from ..schemas import PartnerGet


class PartnerActionException(Exception):
    pass


class PartnerAlreadyExists(Exception):
    """Raises if partner with provided name already exists."""


class PartnerNotFound(Exception):
    """Raises if partner with provided ID not found."""


class PartnersCanNotBeDeleted(Exception):
    """Raises if partner deletion was not successful."""


class PartnerCity(tortoise.models.Model):
    partner = fields.ForeignKeyField("versions.Partner")
    city = fields.ForeignKeyField("versions.City")

    class Meta:
        table = 'partners_cities'
        unique_together = (('partner', 'city'),)


class PanValidationMask(tortoise.models.Model):
    partner: fields.ForeignKeyNullableRelation['Partner'] = fields.ForeignKeyField(
        "versions.Partner",
        on_delete=fields.CASCADE,
        null=False,
    )
    pan_mask = fields.CharField(max_length=16, null=False)

    class Meta:
        table = 'pan_validation_masks'
        unique_together = (('partner', 'pan_mask'),)


class Partner(tortoise.models.Model):
    id = fields.IntField(pk=True)
    name_en = fields.CharField(max_length=255, null=True)
    name_kk = fields.CharField(max_length=255, null=True)
    name_ru = fields.CharField(max_length=255, null=True)
    name_zh = fields.CharField(max_length=255, null=True)
    activity_name_ru = fields.CharField(max_length=255, null=True)
    address = fields.CharField(max_length=255, null=True)
    affiliated = fields.BooleanField(null=True)
    article = fields.CharField(max_length=64, null=True)
    identifier = fields.CharField(max_length=12, null=True)
    is_commerce = fields.BooleanField(null=True)
    consent_confirmed = fields.BooleanField(null=True)
    is_government = fields.BooleanField(null=True)
    is_international = fields.BooleanField(null=True)
    leader_data = fields.JSONField(null=True)
    email = fields.CharField(max_length=100, null=True)
    start_work_hour = fields.CharField(min_length=5, max_length=5, null=True)
    end_work_hour = fields.CharField(min_length=5, max_length=5, null=True)
    registration_date = fields.DatetimeField(null=True)
    courier_partner: fields.ForeignKeyNullableRelation['Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )
    credentials = fields.JSONField(null=True)
    liq_decision_date = fields.DateField(null=True)
    liq_date = fields.DateField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    # type hints
    dispatchers: fields.ReverseRelation['models.ProfileDispatcher']
    leader: fields.ReverseRelation['models.ProfileOwner']
    managers: fields.ReverseRelation['models.ProfileManager']
    service_managers: fields.ReverseRelation['models.ProfileServiceManager']
    branch_managers: fields.ReverseRelation['models.ProfileBranchManager']
    items: fields.ReverseRelation['models.Item']
    orders: fields.ReverseRelation['models.Order']
    couriers: fields.ReverseRelation['models.ProfileCourier']
    settings: fields.ReverseRelation['PartnerSetting']
    courier_partner_id: int
    type = fields.CharEnumField(
        **enums.PartnerType.to_kwargs(default=enums.PartnerType.TOO.value)
    )
    cities = fields.ManyToManyField(
        'versions.City',
        related_name='partners',
        through='partners_cities'
    )

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'partner'
        ordering = ('-created_at',)
        unique_together = (
            ('identifier', 'courier_partner_id'),
            ('name_ru', 'courier_partner_id'),
            ('name_kk', 'courier_partner_id'),
            ('name_en', 'courier_partner_id'),
            ('email', 'courier_partner_id'),
        )

    @property
    def name(self):
        locale = locale_context.get()
        return getattr(self, f'name_{locale}', self.name_en) or self.name_ru

    def __str__(self):
        return f'{self.id} - {self.name_ru}'

    @classmethod
    async def get_partner(cls, partner_id: int) -> 'Partner':
        partner = await cls.filter(id=partner_id).first()
        if not partner:
            raise models.PartnerNotFound(f'Partner with id={partner_id} was not found')
        return partner


async def partner_get(
    partner_id: int,
    with_info: bool = True,
    **kwargs,
) -> dict:
    try:
        partner = await Partner.get(id=partner_id).prefetch_related(
            'cities',
            Prefetch(
                relation='shipment_points',
                queryset=PartnerShipmentPoint.all().select_related('partner', 'city__country'),
            ),
        )
        partner_dict = PartnerGet.from_orm(partner).dict()
        if with_info:
            partner_dict['quantity_products'] = await partner.items.all().count()
            partner_dict['quantity_managers'] = await partner.managers.all().count()
            partner_dict['quantity_orders'] = await partner.orders.all().count()
            partner_dict['quantity_couriers'] = await partner.couriers.filter(
                status=enums.InviteStatus.ACCEPTED.value,
                user__is_active=True,
            ).count()

            partner_dict['history'] = await models.history_get_list(
                model_type='Partner',
                model_id=partner_id,
            )
        return partner_dict
    except tortoise.exceptions.DoesNotExist as e:
        raise PartnerNotFound(
            f'Partner with provided ID: {partner_id} not found',
        ) from e
    except tortoise.exceptions.IntegrityError as e:
        raise PartnerActionException(
            exceptions.get_exception_msg(e),
        ) from e


async def partner_get_list(**kwargs) -> list:
    city_id = kwargs.pop('city_id', None)
    filtered_partners_ids = await Partner.filter(
        **kwargs).values_list('id', flat=True)
    kwargs = {}
    if city_id:
        kwargs['place__city_id'] = city_id
    return [
        await partner_get(partner_id=partner_id, **kwargs) for partner_id in
        filtered_partners_ids
    ]


async def partner_get_many(partner_id_list: typing.List[int]) -> list:
    return await Partner.filter(id__in=partner_id_list).values_list(
        'id', flat=True)


@utils.save_in_history(
    request_method=enums.RequestMethods.POST,
    model_type=enums.HistoryModelName.PARTNER,
)
@atomic()
async def partner_create(
    partner: schemas.PartnerCreate,
    courier_partner_id=None,
    current_user: schemas.UserCurrent = None,
) -> schemas.PartnerGet:
    try:
        partner_dict = partner.credentials.dict()
        if not partner_dict.get('article'):
            article = helpers.ArticleGenerator.generate_article(
                data=partner_dict,
                acronym_list=await Partner.all().values_list('article', flat=True)
            )
            partner_dict['article'] = article

        if courier_partner_id:
            partner_dict['courier_partner_id'] = courier_partner_id
        partner_dict['identifier'] = partner.identifier
        partner_dict['type'] = partner.type
        city_objects = await City.filter(id__in=partner_dict.pop('cities', [-1]))
        partner_created = await Partner.create(**partner_dict)
        await PartnerSetting(partner_id=partner_created.id)
        if city_objects:
            await partner_created.cities.add(*city_objects)
        await partner_created.fetch_related('cities', 'shipment_points')
        return schemas.PartnerGet.from_orm(partner_created)
    except (
        tortoise.exceptions.IntegrityError,
        tortoise.exceptions.DoesNotExist,
    ) as e:
        raise PartnerActionException(
            exceptions.get_exception_msg(e),
        ) from e


@utils.save_in_history(
    request_method=enums.RequestMethods.PUT,
    model_type=enums.HistoryModelName.PARTNER,
)
@tortoise.transactions.atomic()
async def partner_update(
    partner_id: int,
    default_filters: list,
    update: schemas.PartnerUpdate,
) -> dict:
    try:
        partner = await Partner.filter(*default_filters).select_for_update().get(id=partner_id)
        update_dict = update.dict(exclude_unset=True)
        if (cities := update_dict.pop('cities', None)) is not None:
            await partner.cities.clear()
            cities_obj = await City.filter(id__in=cities)
            await partner.cities.add(*cities_obj)

        await partner.update_from_dict(update_dict).save()

        return await partner_get(partner_id)

    except tortoise.exceptions.IntegrityError as e:
        raise PartnerActionException(
            exceptions.get_exception_msg(e),
        ) from e


@utils.save_in_history(
    request_method=enums.RequestMethods.POST,
    model_type=enums.HistoryModelName.PARTNER,
)
@tortoise.transactions.atomic()
async def delivery_service_create(
    partner: schemas.DeliveryServiceCreate,
):
    verification_partner = await verification.client.verify_partner(
        schemas.VerificationPartner(
            identifier=partner.identifier,
            confirmed=True,
        )
    )

    partner_created = await partner_create(
        partner=schemas.PartnerCreate(
            identifier=partner.identifier,
            credentials=verification_partner.get('credentials')
        ),
    )

    await models.new_profile_create(profile=schemas.ProfileCreate(
        user=schemas.UserCreate(phone_number=partner.service_manager_phone_number),
        profile_content={'partner_id': partner_created['id']},
        profile_type=enums.ProfileType.SERVICE_MANAGER,
    ))

    return partner_created


@utils.save_in_history(
    request_method=enums.RequestMethods.POST,
    model_type=enums.HistoryModelName.PARTNER,
)
@tortoise.transactions.atomic()
async def delivery_service_create(
    partner: schemas.DeliveryServiceCreate,
):
    verification_partner = {}
    if partner.type == enums.PartnerType.TOO and not partner.name_ru:
        verification_partner = await verification.client.verify_partner(
            schemas.VerificationPartner(
                bin=partner.identifier,
                confirmed=True,
            )
        )

    partner_created = await partner_create(
        partner=schemas.PartnerCreate(
            identifier=partner.identifier,
            type=partner.type,
            credentials=(
                verification_partner.get(
                    'credentials', {'name_ru': partner.name_ru}
                )
            )
        ),
    )

    await models.new_profile_create(profile=schemas.ProfileCreate(
        user=schemas.UserCreate(phone_number=partner.service_manager_phone_number),
        profile_content={'partner_id': partner_created['id']},
        profile_type=enums.ProfileType.SERVICE_MANAGER,
    ))
    return partner_created


@utils.save_in_history(
    request_method=enums.RequestMethods.DELETE,
    model_type=enums.HistoryModelName.PARTNER,
)
async def partner_delete(
    partner_id: int,
    current_user: schemas.UserCurrent,
) -> None:
    try:
        await partner_ensure_exists(partner_id)
        await Partner.filter(id=partner_id).delete()

    except tortoise.exceptions.IntegrityError as e:
        raise PartnerActionException(
            exceptions.get_exception_msg(e),
        ) from e


@utils.save_in_history(
    request_method=enums.RequestMethods.DELETE,
    model_type=enums.HistoryModelName.PARTNER,
)
async def partner_delete_bulk(
    partner_id_list: typing.List[int],
    current_user: schemas.UserCurrent,
) -> None:
    try:
        await Partner.filter(id__in=partner_id_list).delete()
    except tortoise.exceptions.IntegrityError as e:
        raise PartnersCanNotBeDeleted(
            'Partners with provided id list cannot be deleted',
        ) from e


async def partner_ensure_exists(partner_id: int) -> None:
    partner = await partner_get(partner_id)
    if not partner:
        raise PartnerNotFound(
            f'Partner with provided ID: {partner_id} not found',
        )


async def get_partner_cities(
    partner_id: int, country_id: int | None = None
) -> list['City']:

    partner = await Partner.get_partner(partner_id)
    q_objects = []
    if country_id:
        q_objects.append(Q(country_id=country_id))
    cities = await partner.cities.all().filter(Q(*q_objects, join_type='AND'))
    return cities


async def get_partner_countries(partner_id: int) -> list['models.Country']:
    cities = await get_partner_cities(partner_id)
    countries = await models.Country.filter(cities__in=cities).distinct()
    return countries
