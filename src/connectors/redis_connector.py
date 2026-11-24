from typing import Self, cast

import redis.asyncio as redis


class RedisManager:
    def __init__(
        self,
        host: str,
        port: int,
    ):
        self.host = host
        self.port = port
        self.redis : redis.Redis | None = None

    async def connect(self) -> None:
        # self.redis = await redis.Redis(
        #     host=self.host,
        #     port=self.port,
        # )
        client = await redis.Redis(host=self.host, port=self.port)
        # Явно говорим чекеру: "Это точно Redis, а не None"
        self.redis = cast(redis.Redis, client)

    def get_client(self) -> redis.Redis:
        """Возвращает подключенный клиент Redis."""
        if self.redis is None:
            raise RuntimeError("Redis не подключен. Вызовите connect() сначала.")
        return self.redis


    # ---------- контекстный менеджер ----------

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    # ---------- команды ----------

    async def set(self, key: str, value: str, expire: int | None = None):
        if self.redis is None:
            raise RuntimeError("Redis не подключен. Вызовите connect() сначала.")

        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        if self.redis is None:
            raise RuntimeError("Redis не подключен. Вызовите connect() сначала.")
        return await self.redis.get(key)

    async def delete(self, key: str) -> int:
        if self.redis is None:
            raise RuntimeError("Redis не подключен. Вызовите connect() сначала.")
        return await self.redis.delete(key)

    async def close(self) -> None:
        if self.redis is not None:
            await self.redis.close()
