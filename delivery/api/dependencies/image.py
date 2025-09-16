from api.utils.image.image_validator import ImageValidator
from api.conf import conf


def get_cancel_image_validator():
    """
    max_size 20 Mb
    """
    return ImageValidator(max_size=conf.media.maximum_size_of_image)


def get_comment_image_validator():
    return ImageValidator(max_size=conf.media.maximum_size_of_image)


__all__ = (
    'get_cancel_image_validator',
    'get_comment_image_validator',
)
