import uuid

from ...conf import conf
from ... import schemas
from .. import common


class BiometryRemoteServiceRequestError(Exception):
    """Raises when remote Biometry service cannot proceed with request."""


class BiometryRemoteServiceResponseError(Exception):
    """Raises when remote Biometry service returns response with `ERROR` status."""


class Biometry(common.AsyncHTTPSession):
    def __init__(self):
        self.url = conf.biometry.url
        super().__init__()

    async def get_biometry_url(self, biometry_request: schemas.BiometryRequest) -> str:
        query = f"{self.url}request-matching"
        request_data = biometry_request.dict()
        request_data['state'] = str(uuid.uuid4())
        resp = await self._async_session.post(
            url=query, json=request_data
        )
        data = await resp.json()
        if not data:
            raise BiometryRemoteServiceRequestError('Service biometry is not available!')

        if data and data.get('url') is None:
            raise BiometryRemoteServiceResponseError(data)
        return data
