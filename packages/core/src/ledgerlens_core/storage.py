"""S3-compatible object store (MinIO locally, S3/R2 in production) and the key layout."""

from __future__ import annotations

import uuid
from functools import lru_cache
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from ledgerlens_core.settings import get_settings


class keys:
    """Object-key layout from plan §2 (Slice A step 3). Pure functions, no I/O."""

    @staticmethod
    def page(tenant_id: uuid.UUID, document_id: uuid.UUID, number: int) -> str:
        return f"pages/{tenant_id}/{document_id}/{number}.png"

    @staticmethod
    def ocr(tenant_id: uuid.UUID, document_id: uuid.UUID, number: int) -> str:
        return f"pages/{tenant_id}/{document_id}/{number}.ocr.json"

    @staticmethod
    def artifact(model_version_id: uuid.UUID, name: str) -> str:
        return f"artifacts/{model_version_id}/{name}"

    @staticmethod
    def report(model_version_id: uuid.UUID, name: str) -> str:
        return f"reports/{model_version_id}/{name}"

    @staticmethod
    def dataset(dataset_id: uuid.UUID, name: str) -> str:
        return f"datasets/{dataset_id}/{name}"

    @staticmethod
    def job_log(job_id: uuid.UUID) -> str:
        return f"jobs/{job_id}/log.txt"


class ObjectStore:
    def __init__(self, client: Any, bucket: str) -> None:
        self._client = client
        self._bucket = bucket
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def put(self, key: str, data: bytes, *, content_type: str = "application/octet-stream") -> str:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)
        return key

    def get(self, key: str) -> bytes:
        body = self._client.get_object(Bucket=self._bucket, Key=key)["Body"]
        return bytes(body.read())

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError:
            return False
        return True

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def list_keys(self, prefix: str) -> list[str]:
        paginator = self._client.get_paginator("list_objects_v2")
        keys: list[str] = []
        for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
            keys.extend(o["Key"] for o in page.get("Contents", []))
        return keys

    def presigned_get(self, key: str, *, expires_in: int = 600) -> str:
        url: str = self._client.generate_presigned_url(
            "get_object", Params={"Bucket": self._bucket, "Key": key}, ExpiresIn=expires_in
        )
        return url


@lru_cache(maxsize=1)
def get_object_store() -> ObjectStore:
    s = get_settings()
    client = boto3.client(
        "s3",
        endpoint_url=s.object_store_endpoint,
        aws_access_key_id=s.object_store_access_key,
        aws_secret_access_key=s.object_store_secret_key.get_secret_value(),
        region_name="us-east-1",
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )
    return ObjectStore(client, s.object_store_bucket)
