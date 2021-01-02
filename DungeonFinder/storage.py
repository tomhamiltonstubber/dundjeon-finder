import logging
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage

tc_logger = logging.getLogger('df.storage')


class S3PublicStorage(S3Boto3Storage):
    def __init__(self, **s3_settings):
        s3_settings.update(
            bucket_name=settings.AWS_PUBLIC_BUCKET_NAME,
            object_parameters={'CacheControl': 'max-age=86400'},
        )
        super().__init__(**s3_settings)


class FSPublicStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None, **s3_settings):
        tmp_loc = os.path.join(settings.MEDIA_ROOT, 'public/')
        tmp_url = settings.PUBLIC_URL
        super().__init__(location=tmp_loc, base_url=tmp_url, **s3_settings)


if settings.LIVE:  # pragma no branch
    PublicStorage = S3PublicStorage
else:
    PublicStorage = FSPublicStorage
