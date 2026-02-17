import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from ..core.config import settings


s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
    region_name=settings.s3_region,
    config=Config(signature_version="s3v4"),
)


def ensure_bucket():
    buckets = s3.list_buckets().get("Buckets", [])
    if not any(b["Name"] == settings.s3_bucket for b in buckets):
        s3.create_bucket(Bucket=settings.s3_bucket)


def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream"):
    s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type)


def public_url(key: str) -> str:
    return f"{settings.s3_public_url}/{key}"


def download_bytes(key: str) -> bytes:
    obj = s3.get_object(Bucket=settings.s3_bucket, Key=key)
    body = obj.get("Body")
    return body.read() if body else b""


def delete_key(key: str):
    try:
        s3.delete_object(Bucket=settings.s3_bucket, Key=key)
    except ClientError:
        pass
