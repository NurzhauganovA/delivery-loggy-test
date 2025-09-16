import enum

from . import descriptor


class VerificationEntity(str, enum.Enum):
    USER = 'user'
    PARTNER = 'partner'


class VerificationStatusCode(str, enum.Enum):
    SCSE001 = 'SCSE001'
    SCSS001 = 'SCSS001'
    FAULT015 = 'FAULT015'


class SMSActions(descriptor.Descriptor):
    REGISTRATION = ('Компания Jedel приглашает вас зарегистрироваться '
                    'в качестве курьера. Если вы согласны то пройдите '
                    'по данной ссылке: {}')
    BIOMETRY = 'Ссылка на видеоидентификацию: {}'
    FEEDBACK = 'Уважаемый(-ая) {}, просим перейти по ссылке для оценки работы курьера: {}'
    MONITORING = 'Уважаемый(-ая) {}, Ваша посылка {} от {} уже в пути. Вы можете отслеживать ее перейдя по ссылке: {}'
