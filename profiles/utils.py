import logging
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger('profiles')


class ImageUploadUtility:
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    ALLOWED_FORMATS = ['JPEG', 'JPG', 'PNG', 'WEBP']
    MAX_DIMENSIONS = (1200, 1200)
    QUALITY = 85

    @staticmethod
    def validate_image(image_file):
        if image_file.size > ImageUploadUtility.MAX_FILE_SIZE:
            max_size_mb = ImageUploadUtility.MAX_FILE_SIZE / (1024 * 1024)
            current_size_mb = image_file.size / (1024 * 1024)

            raise ValidationError(
                _(
                    'Image file size cannot exceed {max_size}MB. '
                    'Current size: {current_size}MB'
                ).format(
                    max_size=max_size_mb,
                    current_size=f'{current_size_mb:.2f}',
                )
            )

        try:
            img = Image.open(image_file)
            img.verify()

            image_file.seek(0)
            img = Image.open(image_file)

            if img.format.upper() not in ImageUploadUtility.ALLOWED_FORMATS:
                raise ValidationError(
                    _(
                        'Invalid image format. Allowed formats: {formats}'
                    ).format(
                        formats=', '.join(ImageUploadUtility.ALLOWED_FORMATS)
                    )
                )

        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                str(_('Image validation failed')),
                extra={
                    'error': str(e),
                    'exception_type': type(e).__name__,
                    'file_name': image_file.name,
                    'file_size': image_file.size,
                },
            )
            raise ValidationError(
                _('Invalid image file: {error}').format(error=str(e))
            )

        return True

    @staticmethod
    def process_image(image_file, max_dimensions=None, quality=None):
        if max_dimensions is None:
            max_dimensions = ImageUploadUtility.MAX_DIMENSIONS
        if quality is None:
            quality = ImageUploadUtility.QUALITY

        ImageUploadUtility.validate_image(image_file)

        try:
            image_file.seek(0)
            img = Image.open(image_file)

            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(
                    img,
                    mask=img.split()[-1] if img.mode == 'RGBA' else None,
                )
                img = background

            img.thumbnail(max_dimensions, Image.Resampling.LANCZOS)

            output = BytesIO()
            img_format = (
                'JPEG'
                if img.format in ['JPEG', 'JPG'] or img.format is None
                else img.format
            )
            img.save(
                output,
                format=img_format,
                quality=quality,
                optimize=True,
            )
            output.seek(0)

            return InMemoryUploadedFile(
                output,
                'ImageField',
                f"{image_file.name.split('.')[0]}.{img_format.lower()}",
                f'image/{img_format.lower()}',
                output.tell(),
                None,
            )

        except ValidationError:
            raise
        except Exception as e:
            logger.exception(
                str(_('Image processing failed')),
                extra={
                    'error': str(e),
                    'exception_type': type(e).__name__,
                    'file_name': image_file.name,
                    'file_size': image_file.size,
                },
            )
            raise ValidationError(
                _('Invalid image file: {error}').format(error=str(e))
            )

    @staticmethod
    def get_image_dimensions(image_file):
        image_file.seek(0)
        img = Image.open(image_file)
        return img.size
