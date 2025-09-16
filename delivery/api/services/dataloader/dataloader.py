import asyncio
import typing
import uuid

from ...conf import conf
from .. import common


class DataloaderRemoteServiceRequestError(Exception):
    """Raises when remote Dataloader service cannot proceed with request."""


class DataloaderRemoteServiceResponseError(Exception):
    """Raises when remote Dataloader service returns response with `ERROR` status."""


class DataloaderDontConfigured(Exception):
    """Raises when dataloader don't configure"""


class Dataloader(common.AsyncHTTPSession):
    def __init__(self):
        self.url = conf.dataloader.url
        self.current_user_id = None

        super().__init__()


    @staticmethod
    async def wait_for_complete(*tasks, timeout=2):
        combined = asyncio.gather(*tasks)
        try:
            await asyncio.wait_for(combined, timeout=timeout)
            return [t.result() for t in tasks]
        except asyncio.TimeoutError:
            return [t.result() if t.done() else 'Timeout'
                    for t in tasks]


    @staticmethod
    async def catch_errors(data):

        try:
            if data and data['status'] == 'SERVICE_UNAVAILABLE':
                raise DataloaderRemoteServiceRequestError(
                    'Service dataloader is not available!')
            if data and data['status'] != 'SUCCESS':
                raise DataloaderRemoteServiceResponseError(data['error_description'])
        except KeyError:
            raise DataloaderRemoteServiceRequestError('Could not verify provided data')

        return data['data']


    async def send_post_request(
        self,
        query: str,
        data: dict,
        error_handler: typing.Callable,
    ) -> dict:

        resp = await self._async_session.recorded_post(
            url=query,
            json=data
        )
        resp_data = await resp.json()
        await error_handler(resp_data)

        return resp_data

    async def __check_in_forbidden_services(self, requisite: str) -> str:
        query = f"{self.url}pkb/additional"
        body = {'iin': requisite, 'subject_identifier': str(uuid.uuid4())}
        data = await self.send_post_request(query, body, Dataloader.catch_errors)

        return data['data']

    async def get_user_data(self, iin: str) -> str:
        query = f"{self.url}gkb/gbdfl"
        body = {'iin': iin, 'subject_identifier': str(uuid.uuid4())}
        data = await self.send_post_request(query, body, Dataloader.catch_errors)

        return data['data']

    async def get_partner_data(self, _bin: str):
        query = f"{self.url}gkb/gbdul"
        body = {'bin': _bin, 'subject_identifier': str(uuid.uuid4())}

        data = await self.send_post_request(query, body, Dataloader.catch_errors)
        return data['data']

    async def partner_verification(self, bin_: str):
        services = ['KGD03', 'KGD22', 'KGD18', 'KGD12', 'KGD02', 'KFM01']
        partner_services_list = await self.__check_in_forbidden_services(bin_)

        partner_in = (
            list(set(services) & set(partner_services_list['subject_present_services']))
        )
        return partner_in

    async def user_verification(self, iin: str):
        services = ['KGD05', 'KGD15', 'KFM01', 'KPS01', 'KGD01', 'KGD22']
        users_service_list = await self.__check_in_forbidden_services(iin)
        user_in = (
            list(set(services) & set(users_service_list['subject_present_services']))
        )
        return user_in

    async def get_cars_by_iin(self, iin):
        query = f"{self.url}gkb/gbd-auto"
        body = {'iin': iin, 'subject_identifier': str(uuid.uuid4())}
        data = await self.send_post_request(query, body, Dataloader.catch_errors)

        return data['data']

    async def get_user_info(self, iin: str):
        data = await asyncio.wait_for(
            self.get_user_data(iin),
            timeout=conf.dataloader.timeout
        )

        if data and data.get('status') == 'SUBJECT_NOT_FOUND':
            raise DataloaderRemoteServiceResponseError(data['error_description'])

        auto_info = await asyncio.wait_for(
            self.get_cars_by_iin(iin),
            timeout=conf.dataloader.timeout
        )

        users_service_list = await asyncio.wait_for(
            self.user_verification(iin),
            timeout=conf.dataloader.timeout
        )

        return {
            'common': data,
            'user_in': users_service_list,
            'is_hides': True if users_service_list else False,
            'auto': auto_info
        }


    async def get_partner_info(self, _bin: str):
        data = await asyncio.wait_for(
            self.get_partner_data(_bin),
            timeout=conf.dataloader.timeout
        )
        if data and data.get('status').get('code') not in ('002',):
            raise DataloaderRemoteServiceResponseError(data['status']['name_ru'])

        verification_data = await asyncio.wait_for(
            self.partner_verification(_bin),
            timeout=conf.dataloader.timeout
        )

        if verification_data:
            data['partner_in'] = verification_data

        return data
