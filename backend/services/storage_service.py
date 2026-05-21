"""File storage: local disk (default) or S3-compatible cloud when configured."""

from __future__ import annotations

import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from core.config import settings

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, stream: BinaryIO, content_type: str | None = None) -> str:
        """Persist file and return a public or app-served URL."""

    @abstractmethod
    def save_bytes(self, key: str, data: bytes, content_type: str | None = None) -> str:
        ...


class LocalStorageBackend(StorageBackend):
    def __init__(self, root: str | None = None):
        self.root = Path(root or settings.UPLOAD_DIR)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, key: str, stream: BinaryIO, content_type: str | None = None) -> str:
        dest = self._path(key)
        with open(dest, "wb") as out:
            shutil.copyfileobj(stream, out)
        return f"{PUBLIC_BASE_URL}/uploads/{key}"

    def save_bytes(self, key: str, data: bytes, content_type: str | None = None) -> str:
        dest = self._path(key)
        dest.write_bytes(data)
        return f"{PUBLIC_BASE_URL}/uploads/{key}"


class S3StorageBackend(StorageBackend):
    """Optional cloud storage (AWS S3, MinIO, etc.)."""

    def __init__(self):
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError(
                "S3 storage requires boto3: pip install boto3"
            ) from exc

        self.bucket = os.environ["S3_BUCKET"]
        self.client = boto3.client(
            "s3",
            endpoint_url=os.getenv("S3_ENDPOINT_URL"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        self.public_base = os.getenv(
            "S3_PUBLIC_BASE_URL",
            f"https://{self.bucket}.s3.amazonaws.com",
        ).rstrip("/")

    def save(self, key: str, stream: BinaryIO, content_type: str | None = None) -> str:
        extra = {"ContentType": content_type} if content_type else {}
        self.client.upload_fileobj(stream, self.bucket, key, ExtraArgs=extra)
        return f"{self.public_base}/{key}"

    def save_bytes(self, key: str, data: bytes, content_type: str | None = None) -> str:
        import io

        return self.save(key, io.BytesIO(data), content_type)


def get_storage() -> StorageBackend:
    if STORAGE_BACKEND == "s3":
        return S3StorageBackend()
    return LocalStorageBackend()


def unique_key(original_filename: str, prefix: str = "") -> str:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe = "".join(c if c.isalnum() or c in ".-_" else "_" for c in original_filename)
    if prefix:
        return f"{prefix}/{ts}_{safe}"
    return f"{ts}_{safe}"
