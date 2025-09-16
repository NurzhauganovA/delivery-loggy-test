from json import dumps
from .. import common
from ...conf import conf
from ... import schemas


class FirebaseInvalidRegistrationError(Exception):
    """Raises if invalid registration token given to message"""


class Firebase(common.AsyncHTTPSession):
    def __init__(self, headers=None):
        if not headers:
            headers = {
                'Authorization': conf.firebase.server_key,
                'Content-Type': 'application/json'
            }
        super().__init__(headers=headers)

    async def send(self, message: schemas.FirebaseMessage):
        data = dumps(message.dict(exclude_unset=True, exclude_none=True))
        resp = await self._async_session.post(
            url=f'https://fcm.googleapis.com/fcm/send',
            data=data,
        )

        resp_data = await resp.json()
        await self.catch_errors(resp_data)

    async def catch_errors(self, resp: dict):
        # TODO: delete device tokens if any error occurred.
        pass
