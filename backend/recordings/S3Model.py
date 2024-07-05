import io

from aiobotocore.session import get_session
from contextlib import asynccontextmanager

from datetime import datetime

import os

class S3Client:
    def __init__(self, AccessKey: str, SecretKey: str, Endpoint: str, BucketName: str):
        self.config = {
            "aws_access_key_id": AccessKey,
            "aws_secret_access_key": SecretKey,
            "endpoint_url": Endpoint
        }
        self.bucket = BucketName
        self.session = get_session()

    @asynccontextmanager
    async def get_S3_client(self):
        async with self.session.create_client("S3", **self.config) as Client:
            yield Client

    async def push_file(self, FileData: bytes, UserId: int) -> str:

        url = f'local_save/{UserId}{datetime.now()}.wav'

        f = open(url, 'wb')
        f.write(FileData)
        f.close()

        return url

    async def get_file(self, url: str):
        return open(url, 'rb').read()