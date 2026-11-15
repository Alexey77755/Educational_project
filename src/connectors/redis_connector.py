from typing import Self

import redis.asyncio as redis


class RedisManager:
    def __init__(
        self,
        host: str,
        port: int,
    ):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self) -> None:
        self.redis = await redis.Redis(
            host=self.host,
            port=self.port,
        )

    # ---------- контекстный менеджер ----------

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    # ---------- команды ----------

    async def set(self, key: str, value: str, expire: int | None = None):
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str) -> int:
        return await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
