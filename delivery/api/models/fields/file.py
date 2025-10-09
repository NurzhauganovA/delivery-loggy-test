import base64
import imghdr
import io
import os
import typing
import uuid
from datetime import datetime
from pathlib import Path

import PIL.Image as Image
from starlette.datastructures import UploadFile
from tortoise import ConfigurationError
from tortoise.fields import TextField

from api.conf import conf
from api.exceptions import HTTPBadRequestException
from api.utils.file import File


class FileValidationError(HTTPBadRequestException):
    pass


class FileField(TextField):
    def __init__(self, *, upload_to: str, allowed_extensions: list = None, **kwargs):
        super().__init__(**kwargs)
        upload_to = datetime.now().strftime(upload_to)
        if not os.path.exists(conf.media.root):
            raise ConfigurationError(f'No such a directory: {conf.media.root}')
        if upload_to in conf.media.url:
            raise ConfigurationError(f'Upload to folder can not be same as media url')
        os.makedirs(conf.media.root / upload_to, exist_ok=True)
        self.ALLOWED_EXTENSIONS = allowed_extensions if allowed_extensions else [
            'jpg', 'jpeg', 'png', 'svg', 'csv', 'doc', 'docx', 'txt',
        ]

        self.upload_to = Path(upload_to)

    def validate_file(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        if file_extension[1:] not in self.ALLOWED_EXTENSIONS:
            os.remove(conf.media.root / file_path)
            raise FileValidationError(f'Invalid file extension: {file_extension}. '
                                      f'Allowed extensions are: {", ".join(self.ALLOWED_EXTENSIONS)}')

    def to_db_value(self, value: typing.Union[str, UploadFile, bytes],
                    instance):
        if isinstance(value, str):
            return value.replace(conf.media.url + '/', '')
        elif isinstance(value, UploadFile):
            return self.save_file_from_fastapi(value)
        elif isinstance(value, File):
            return self.save_file(value)
        elif isinstance(value, bytes):
            return self.save_file_from_base64(value)
        return value

    def to_python_value(self, value: typing.Union[str, UploadFile, bytes]):
        path = ''
        if isinstance(value, str):
            path = value
        elif isinstance(value, UploadFile):
            path = self.save_file_from_fastapi(value)
        elif isinstance(value, File):
            path = self.save_file(value)
        elif isinstance(value, bytes):
            path = self.save_file_from_base64(value)
        if path:
            return f'{conf.media.url}/{path}'

    def save_file_from_base64(self, value):
        file_path = self.upload_to / f'{uuid.uuid4()}.jpg'
        im = Image.open(io.BytesIO(base64.b64decode(value)))
        im.save(conf.media.root / file_path, 'JPEG')
        self.validate_file(file_path)
        return f'{file_path}'

    def save_file_from_fastapi(self, value: UploadFile):
        file = value.file
        file_ext = value.filename.split('.')[-1]
        file_name = f'{uuid.uuid4()}.{file_ext}'
        file_path = self.upload_to / file_name

        with open(conf.media.root / file_path, 'wb') as f:
            f.write(file.read())
        self.validate_file(file_path)
        return f'{file_path}'

    def save_file(self, file: File):
        file_ext = file.ext
        file_name = f'{uuid.uuid4()}.{file_ext}'
        file_path = self.upload_to / file_name

        with open(conf.media.root / file_path, 'wb') as f:
            f.write(file.bytes)
        self.validate_file(file_path)
        return f'{file_path}'


class ImageField(FileField):
    def validate_file(self, file_path):
        self.ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
        super(ImageField, self).validate_file(file_path)
        file_type = imghdr.what(conf.media.root / file_path)
        if file_type not in self.ALLOWED_EXTENSIONS:
            os.remove(conf.media.root / file_path)
            raise FileValidationError(f'Invalid file type: {file_type}. '
                                      f'Allowed types are: {", ".join(self.ALLOWED_EXTENSIONS)}')
