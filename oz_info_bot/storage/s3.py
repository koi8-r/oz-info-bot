from typing import Optional

from aiobotocore.session import get_session, ClientCreatorContext
from types_aiobotocore_s3.client import S3Client
from types_aiobotocore_s3.paginator import ListObjectsPaginator

from oz_info_bot.storage.base import AbcStorage


class S3IdStorage(AbcStorage[str, bytes]):
    access_key: str
    secret_key: str
    url: str

    def __init__(self, bucket: str, key: str, secret: str, url: str) -> None:
        super().__init__()
        self.bucket = bucket
        self.access_key, self.secret_key, self.url = key, secret, url
        self.sess = get_session()

    @property
    def ua(self) -> ClientCreatorContext:
        return self.sess.create_client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.url,
        )

    async def put(self, k: str, v: Optional[bytes]) -> None:
        async with self.ua as s3:
            s3: S3Client
            await s3.put_object(
                Bucket=self.bucket,
                Key=k,
                Body=v,
                ContentType='application/octet-stream',
            )

    async def get(self, k: str) -> Optional[bytes]:
        async with self.ua as s3:
            s3: S3Client
            o = await s3.get_object(Bucket=self.bucket, Key=k)
            async with o['Body'] as stream:
                return await stream.read()

    async def rm(self, k: str) -> None:
        raise NotImplemented

    async def aiter_wrapper(self):
        async with self.ua as s3:
            s3: S3Client
            # list_objects_v2
            paginator: ListObjectsPaginator = s3.get_paginator('list_objects')
            async for p in paginator.paginate(
                Bucket=self.bucket, Prefix='/',
            ):
                for c in p.get('Contents', []):
                    yield c['Key']

    def __aiter__(self):
        return self.aiter_wrapper()

