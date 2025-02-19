from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class EventMediaStorage(S3Boto3Storage):
    location = 'events'
    file_overwrite = True
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME

class EventGalleryStorage(S3Boto3Storage):
    location = 'events/gallery'
    file_overwrite = True
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME