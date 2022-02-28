from storages.backends.s3boto3 import S3Boto3Storage
from .settings import *

# class MediaStorage(S3Boto3Storage):
#     location = 'media'
#     file_overwrite = False


class PublicMediaStorage(S3Boto3Storage):
    location = AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False
    default_acl = 'public-read'

