import boto3
from botocore.client import Config
from config import settings

s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
    region_name=settings.s3_region,
    config=Config(signature_version="s3v4"),
)


def upload_bytes(key: str, data: bytes, content_type: str = "audio/mpeg"):
    s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type)
