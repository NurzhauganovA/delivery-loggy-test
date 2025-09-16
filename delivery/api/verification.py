# TODO: make grpcio client/service implementation

from datetime import datetime
from . import models
from . import schemas
from . import services


class VerificationEntityNotFound(Exception):
    """Raises if requested user or partner was not found."""


class VerificationResourceNotAvailable(Exception):
    """Raises if remote resource is not available."""


class VerificationService:
    def get_reg_address(self, reg_address_data: dict) -> str:
        result = ''
        if reg_address_data:
            flat = reg_address_data.get('flat')
            result += f'{reg_address_data["district"]}, ' \
                      f'{reg_address_data["street"]}, ' \
                      f'{reg_address_data["building"]}'

            if flat:
                result += f', кв {flat}'

        return result

    def join_dicts_of_dict(self, dict_: dict) -> dict:
        res = {}
        for i in dict_.values():
            res.update(i)

        return res

    def fill_courier_creds(
        self,
        courier_creds: dict,
        data: dict
    ) -> None:
        for key in courier_creds.keys():
            courier_creds[key] = data.get(key)

    def check_if_user_in_non_allowed_orgs(self, user_info: dict) -> bool:
        non_allowed_orgs = ['KGD05', 'KPS01']
        if list(set(user_info["user_in"]) & set(non_allowed_orgs)):
            return True

    async def verify_courier(
        self,
        courier: schemas.VerificationCourier,
    ) -> dict:
        user = await models.user_get(iin=courier.iin)

        dataloader = services.dataloader.service
        verification_data = await dataloader.get_user_info(courier.iin)
        auto_info = [
            {
                'auto_category': auto.get('auto_category'),
                'vin': auto.get('vin'),
                'auto_model': auto.get('auto_model', ''),
                'special_marks': auto.get('special_marks'),
                'auto_reg_num': auto.get('auto_reg_num'),
            } for auto in verification_data['auto']
        ]

        common_data = verification_data['common']
        courier_creds = dict.fromkeys((
            'birth_date',
            'resident',
            'document_type',
            'document_number',
            'document_exp_date',
            'document_issue_org',
        ), None)

        courier_creds['is_hides'] = self.check_if_user_in_non_allowed_orgs(verification_data)
        self.fill_courier_creds(courier_creds, common_data)
        courier_creds['auto'] = auto_info
        courier_creds['reg_address'] = self.get_reg_address(common_data['reg_address'])
        courier_creds['user_in'] = verification_data['user_in']

        first_name = common_data.get('first_name', '')
        last_name = common_data.get('last_name', '')
        middle_name = common_data.get('middle_name', '')
        user_update_schema = schemas.UserUpdate(
            first_name=first_name.capitalize() if first_name else user.get('first_name') or '',
            last_name=last_name.capitalize() if last_name else user.get('last_name') or '',
            middle_name=middle_name.capitalize() if middle_name else user.get(
                'middle_name') or '',
            phone_number=user.get('phone_number', ''),
            iin=user.get('iin', ''),
            is_active=user.get('is_active', False),
            credentials=courier_creds
        )
        await models.user_update(user['id'], user_update_schema)
        verification_data['common']['auto'] = auto_info
        verification_data['common']['user_in'] = verification_data['user_in']
        return verification_data['common']

    async def verify_partner(
        self,
        partner: schemas.VerificationPartner,
    ) -> dict:
        data = await services.dataloader.service.get_partner_info(partner.bin)
        organization = data['organization']
        address = organization['address']
        add_info = organization['add_info']
        partner_fetched = schemas.PartnerFetched(**{
            'name_kk': organization.get('short_name_kk') or organization['full_name_kk'],
            'name_ru': organization.pop('short_name_ru') or organization['full_name_ru'],
            'name_en': organization.pop('short_name_en') or organization['full_name_en'],
            'activity_name_ru': organization['activity']['activity_name_ru'],
            'address': f"{address.get('district_ru')}, "
                       f"{address.get('region_ru')}, "
                       f"{address.get('street_ru')}, "
                       f"{address['building_type'].get('name_ru')}: "
                       f"{address.get('building_number')}",
            'affiliated': add_info['affiliated'],
            'is_commerce': add_info['commerce_org'],
            'is_international': add_info['international'],
            'registration_date': (None if organization.get('registration_date') is None
                                  else datetime.strptime(
                organization.get('registration_date')[:-6], '%Y-%m-%d')),
            'liq_decision_date': data.get('liq_decision_date'),
            'liq_date': data.get('liq_date'),
            'leader_data': {
                'first_name': organization['organization_leader'].get('first_name'),
                'last_name': organization['organization_leader'].get('last_name'),
                'middle_name': organization['organization_leader'].get('middle_name'),
                'iin': organization['organization_leader'].get('iin'),
            },
            'partner_in': data.get('partner_in')
        })
        return {
            'bin': partner.bin, 'credentials': partner_fetched
        }


client = VerificationService()
