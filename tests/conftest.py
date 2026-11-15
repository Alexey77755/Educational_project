# ruff: noqa: I001
import asyncio
import json

import aiofiles
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

import pytest
import pytest_asyncio

from collections.abc import AsyncGenerator
from typing import Any
from database import engine_null_pool
from src.api.dependencies import get_db
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from src.config import settings
from src.database import Base, async_session_maker_null_pool
from src.main import app
from src.models import *
from httpx import ASGITransport, AsyncClient


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest_asyncio.fixture()
async def db():
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with aiofiles.open("tests/mock_hotels.json", encoding="utf-8") as file:
        content = await file.read()
        hotels = json.load(content)

    with aiofiles.open("tests/mock_rooms.json", encoding="utf-8") as file:
        content = await file.read()
        rooms = json.load(content)

    hotelsSchemas = [HotelAdd.model_validate(hotel) for hotel in hotels]
    roomsSchemas = [RoomAdd.model_validate(room) for room in rooms]

    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotelsSchemas)
        await db_.rooms.add_bulk(roomsSchemas)
        await db_.commit()


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    await ac.post(
        "/auth/register",
        json={
            "email": "sobaka@mail.ru",
            "password": "ssds22",
        },
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def authenticated_ac(register_user, ac):
    await ac.post(
        "/auth/login",
        json={
            "email": "sobaka@mail.ru",
            "password": "ssds22",
        },
    )

    assert ac.cookies["access_token"]

    yield ac
