from pathlib import Path
from typing import Dict
from typing import List

from pydantic import BaseSettings
from pydantic import Field

from .enums import SMSProvider


class Firebase(BaseSettings):
    server_key: str = Field('', env='FIREBASE_SERVER_KEY')


class Token(BaseSettings):
    secret_key: str = Field('invalid-secret-key', env='SECRET_KEY')
    access_lifetime: int = Field(15, env='ACCESS_TOKEN_LIFETIME')
    refresh_lifetime: int = Field(60 * 24 * 365, env='REFRESH_TOKEN_LIFETIME')
    front_token: str = Field('invalid_front_token', env='FRONT_TOKEN')


class Monitoring(BaseSettings):
    timeout: int = 90
    ttl: int = 5


class Postgres(BaseSettings):
    host: str = Field('127.0.0.1', env='POSTGRES_HOST')
    port: int = Field(5432, env='POSTGRES_PORT')
    user: str = Field('delivery', env='POSTGRES_USER')
    password: str = Field('delivery', env='POSTGRES_PASSWORD')
    database: str = Field('delivery', env='POSTGRES_DB')
    maxsize: int = 900

    @property
    def uri(self) -> str:
        return f'postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'

    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        skip_defaults: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ):
        d = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        if isinstance(d, dict):
            d['uri'] = self.uri
        return d


class Locale(BaseSettings):
    header_name: str = Field('x-locale')
    default_locale: str = Field('en')
    available_locales: list = Field([
        'en',
        'kk',
        'ru',
        'zh',
    ])


class API(BaseSettings):
    debug: int = Field(1, env='DEBUG')
    log_level: str = Field('debug', env='LOG_LEVEL')
    host: str = Field('0.0.0.0', env='API_HOST')
    port: int = Field(5000, env='API_PORT')
    otp_expiration_time: int = 300
    allow_sms: int = Field(0, env='ALLOW_SMS')
    allow_send_feedback_link: int = Field(0, env='ALLOW_SEND_FEEDBACK_LINK')
    allow_emails: int = Field(1, env='ALLOW_EMAIL')
    main_sms_service_type: str = Field('smstraffic', env='SMS_SERVICE_TYPE')
    postcontrol_sms_service_type: str = Field('dataloader', env='POSTCONTROL_SMS_SERVICE_TYPE')
    reload: bool = Field(1, env='API_RELOAD')
    backend_domain: str = Field('api.devloggy-1.trafficwave.kz', env='BACKEND_DOMAIN')
    locale: Locale = Locale()


class SMS(BaseSettings):
    is_active: bool = Field(False)
    provider: SMSProvider = Field('dataloader')
    dataloader: 'DataLoader'

    class Config:
        use_enum_values = True


class Redis(BaseSettings):
    host: str = Field('127.0.0.1', env='REDIS_HOST')
    port: int = Field(6379, env='REDIS_PORT')

    @property
    def uri(self) -> str:
        return f'redis://{self.host}:{self.port}'

    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        skip_defaults: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ):
        d = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        if isinstance(d, dict):
            d['uri'] = self.uri
        return d


class GeoCoder(BaseSettings):
    timeout: int = 5
    key_2gis: str = Field('rukiqk4169', env='API_KEY')
    url_2gis: str = Field('https://catalog.api.2gis.com/', env='GEOCODER_URL')
    url_osm: str = Field('https://nominatim.openstreetmap.org/', env='OSM_URL')


class OSM(BaseSettings):
    timeout: int = 5
    url: str = Field('https://router.project-osrm.org/', env='OSM_URL')


class DataLoader(BaseSettings):
    timeout: int = 60
    url: str = Field('https://dev-dataloader.trafficwave.kz/', env='DATALOADER_URL')


class Biometry(BaseSettings):
    timeout: int = 5
    url: str = Field('https://dev-biometry.trafficwave.kz/', env='BIOMETRY_URL')


class SMSTraffic(BaseSettings):
    login: str = Field('globerce', env='SMSTRAFFIC_LOGIN')
    password: str = Field('O2oPWfLN', env='SMSTRAFFIC_PASSWORD')


class Credentials(BaseSettings):
    smstraffic: SMSTraffic = SMSTraffic()


class URLs(BaseSettings):
    sms_traffic_url: str = 'https://api.smstraffic.ru/multi.php'
    smstraffic_reserve_url: str = 'https://api2.smstraffic.ru/multi.php'
    dataloader_sms_url: str = Field(
        'https://dev-dataloader.trafficwave.kz/sms-traffic/individual-sms',
        env='DATALOADER_SMS_URL',
    )


class OTP(BaseSettings):
    service_call_timeout: int = 5
    credentials: Credentials = Credentials()
    urls: URLs = URLs()
    sender: str = 'Loggy'


class Connections(BaseSettings):
    @property
    def default(self) -> str:
        postgres = Postgres()
        return postgres.uri

    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        skip_defaults: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ):
        d = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        if isinstance(d, dict):
            d['default'] = self.default
        return d


class Versions(BaseSettings):
    models: List[str] = [
        'api.models',
        'api.modules.call_request.infrastructure.db_table',
        'api.modules.city.infrastructure.db_table',
        'api.modules.delivery_point.infrastructure.db_table',
        'api.modules.order.infrastructure.db_table',
        'api.modules.order_chain.infrastructure.db_table',
        'api.modules.partner_settings.infrastructure.db_table',
        'api.modules.shipment_point.infrastructure.db_table',
        'aerich.models',
    ]
    default_connection: str = 'default'


class Apps(BaseSettings):
    versions: Versions = Versions()


class Tortoise(BaseSettings):
    connections: Connections = Connections()
    apps: Apps = Apps()
    use_tz: bool = False


class Media(BaseSettings):
    root: Path = Field(Path(__file__).resolve().parent.parent / 'media', env='MEDIA_ROOT')
    url: str = Field('/media', env='MEDIA_URL')
    maximum_size_of_image: int = Field(20 * 1024 * 1024, env='MAXIMUM_SIZE_OF_IMAGE') # 20 Mega Bytes


class Static(BaseSettings):
    root: Path = Field(Path(__file__).resolve().parent.parent / 'static', env='STATIC_ROOT')
    url: str = Field('/static', env='STATIC_URL')


class FrontEnd(BaseSettings):
    domain: str = Field('https://courier-front.trafficwave.kz', env='FRONTEND_DOMAIN')
    feedback_url: str = 'orders/{}/feedback'
    monitoring_url: str = 'orders/{}/monitoring'
    merchant_order_link: str = 'merchant/client-form/{}'


class EmailBackend(BaseSettings):
    smtp_server: str = 'smtp.mail.ru'
    port: int = 465
    sender_email: str = 'loggy@trafficwave.kz'
    password: str = 'R%Pro1ou3rYD'


class FreedomBankOTPClientSettings(BaseSettings):
    base_url: str = Field('https://dev-2-all-proxy-in-one.trafficwave.kz/bank/ca/api/otp-service/otp', env='FREEDOM_BANK_OTP_BASE_URL')
    username: str = Field('loggy', env='FREEDOM_BANK_OTP_USERNAME')
    password: str = Field('tNvpwH4HH8GGjPFYtjcEwR==', env='FREEDOM_BANK_OTP_PASSWORD')


class PosTerminalOTPClientSettings(BaseSettings):
    # TODO: Эти переменные должны попадаться в секреты прода перед залитием.
    base_url: str = Field('https://dev-2-all-proxy-in-one.trafficwave.kz/colvir/damu/', env='POS_TERMINAL_OTP_BASE_URL')
    auth_header: str = Field('loggy', env='POS_TERMINAL_OTP_AUTH_HEADER')


class FreedomBankSettings(BaseSettings):
    partner_id: int = Field(131, env='FREEDOM_BANK_KZ_PARTNER_ID')


class FreedomBankCallbacksSettings(BaseSettings):
    token: str = Field("Basic dHJhZmZpY3dhdmU6THJmU04zYnl0eG1ZdWFPN2xDQm5zbFNRaVFmdlM0cDA=", env='FREEDOM_BANK_KZ_CALLBACKS_TOKEN')


class FreedomPOSTerminalRegistrationSettings(BaseSettings):
    base_url: str = Field('https://dev-2-all-proxy-in-one.trafficwave.kz/colvir/damu/tms', env='FREEDOM_POS_TERMINAL_REGISTRATION_BASE_URL')
    token: str = Field('Basic b3ZlcmRyYWZ0OldmbWhldFprbTZDa21qZm9CY2QzcFRRclZ0dEZzNUhU', env='FREEDOM_POS_TERMINAL_REGISTRATION_TOKEN')


class POSTerminalSettings(BaseSettings):
    partner_id: int = Field(142, env='POS_TERMINAL_PARTNER_ID')


class Settings(BaseSettings):
    firebase: Firebase = Firebase()
    token: Token = Token()
    monitoring: Monitoring = Monitoring()
    api: API = API()
    postgres: Postgres = Postgres()
    redis: Redis = Redis()
    geocoder: GeoCoder = GeoCoder()
    osm: OSM = OSM()
    dataloader: DataLoader = DataLoader()
    biometry: Biometry = Biometry()
    otp: OTP = OTP()
    tortoise: Tortoise = Tortoise()
    media: Media = Media()
    static: Static = Static()
    frontend: FrontEnd = FrontEnd()
    email_backend: EmailBackend = EmailBackend()
    freedom_bank_otp: FreedomBankOTPClientSettings = FreedomBankOTPClientSettings()
    freedom_bank: FreedomBankSettings = FreedomBankSettings()
    freedom_bank_callbacks: FreedomBankCallbacksSettings = FreedomBankCallbacksSettings()
    freedom_pos_terminal_registration: FreedomPOSTerminalRegistrationSettings = FreedomPOSTerminalRegistrationSettings()
    pos_terminal_otp: PosTerminalOTPClientSettings = PosTerminalOTPClientSettings()
    pos_terminal: POSTerminalSettings = POSTerminalSettings()

    class Config:
        case_sensitive = False


conf = Settings()

tortoise_orm = conf.dict()['tortoise']
