import imghdr
import typing

import fastapi

from api.utils.file import File
from api.utils.image.exceptions import ImageValidationError


class ImageValidator:
    """
    :param max_size: maximum size of the image to validate in bytes
    """
    def __init__(self, max_size: int, allowed_extensions: typing.List[str] = None):
        if allowed_extensions is None:
            allowed_extensions = ['jpg', 'jpeg', 'png']
        self.__allowed_extensions = allowed_extensions
        self.__max_size = max_size

    async def validate(self, image: fastapi.UploadFile):

        actual_size = len(await image.read())
        await image.seek(0)

        if actual_size > self.__max_size:
            mega_bytes = self.__bytes_to_mega_bytes(actual_size)
            max_size_mega_bytes = self.__bytes_to_mega_bytes(self.__max_size)
            raise ImageValidationError(
                f'Maximum allowed size of the image is {max_size_mega_bytes} MB, actual: {mega_bytes} MB',
            )

        # Recognize image file formats based on their first few bytes.
        file_type = imghdr.what(image.file)
        if file_type not in self.__allowed_extensions:
            raise ImageValidationError(
                f'Invalid file type: {file_type}. Allowed types are: {", ".join(self.__allowed_extensions)}')



    @staticmethod
    async def serialize_image(image: fastapi.UploadFile) -> File:
        serialized_image = File(
            bytes=await image.read(),
            name=image.filename,
        )
        return serialized_image

    @staticmethod
    def __bytes_to_mega_bytes(num_bytes: int) -> str:
        """
        Converts a number of bytes into a human-readable string representation in megabytes.
        """
        num_bytes /= (1024.0 * 1024.0)
        return f'{num_bytes:.2f}'
