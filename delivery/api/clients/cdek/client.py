from functools import wraps
from typing import Callable

from httpx import (
    AsyncClient,
    HTTPStatusError,
    Response,
)

from api.clients.cdek.schemas.create_order.request import CreateOrderRequest
from api.logging_module import logger


class CDEKClient:
    def __init__(
            self,
            base_url: str,
            client_id: str,
            client_secret: str,
    ):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__client = AsyncClient(base_url=base_url)
        self.__token = None

    async def aclose(self) -> None:
        await self.__client.aclose()

    @staticmethod
    def authenticated(func: Callable) -> Callable:
        """
            Декоратор, добавляющий логику установки токена при первом запросе
            и обновления токена при ошибке 401 Unauthorized

            Args:
                func: async метод

            Returns:
                async метод
        """
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Если нет токена (это первый запрос), то запросим его
            if not self.__token:
                self.__token = await self._get_token()

            # Делаем вызов к API CDEK
            try:
                response = await func(self, *args, **kwargs)
            except HTTPStatusError as e:
                # Если получаем ошибку 401 unauthorized
                if e.response.status_code == 401:
                    # То запросим новый токен и повторим вызов к API CDEK
                    self.__token = await self._get_token()
                    response = await func(self, *args, **kwargs)
                # Любую другую ошибку прокидываем выше
                else:
                    raise e

            return response

        return wrapper

    async def _get_token(self) -> str:
        """
            Получение авторизационного токена и сохранение его значения в приватный аттрибут

            Returns:
                Токен
        """
        response = await self.__client.post(
            url="/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.__client_id,
                "client_secret": self.__client_secret,
            },
        )
        return response.json()["access_token"]

    @authenticated
    async def get_location(
            self,
            latitude: float,
            longitude: float,
    ) -> Response:
        """
            Получение локации по координатам

            Args:
                latitude: широта
                longitude: долгота

            Returns:
                httpx Response, где тело ответа:
                    {
                        "code": 44,
                        "city_uuid": "01581370-81f3-4322-9a28-3418adfabd97",
                        "city": "Москва",
                        "fias_guid": "0c5b2444-70a0-4932-980c-b4dc0d3f02b5"
                    }
        """
        response = await self.__client.get(
            url="/location/coordinates",
            params={"latitude": latitude, "longitude": longitude},
            headers={"Authorization": f"Bearer {self.__token}"},
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.bind(
                status_code=response.status_code,
                method="GET",
                url=str(response.url),
                response=response.text,
            ).error(e)
            raise e

        return response

    @authenticated
    async def create_order(
            self,
            request: CreateOrderRequest,
    ) -> Response:
        """
            Создание заявки в CDEK

            Args:
                request: схема CreateOrderRequest

            Returns:
                httpx Response, где тело ответа:
                    {
                        "entity": {
                            "uuid": "549b1ab8-518c-42d0-a14f-57569e3e5d65"
                        },
                        "requests": [
                            {
                                "request_uuid": "a1cd3d9e-b70a-4b09-a3fd-d107b3e630c8",
                                "type": "CREATE",
                                "date_time": "2025-09-09T10:13:21+0000",
                                "state": "ACCEPTED"
                            }
                        ],
                        "related_entities": []
                    }
        """
        body = request.dict()

        response = await self.__client.post(
            url="/orders",
            json=body,
            headers={"Authorization": f"Bearer {self.__token}"},
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.bind(
                status_code=response.status_code,
                method="POST",
                url=str(response.url),
                body=body,
                response=response.text,
            ).error(e)
            raise e

        return response
