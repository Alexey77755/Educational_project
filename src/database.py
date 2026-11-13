from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(settings.DB_URL)
engine_null_pool = create_async_engine(settings.DB_URL,poolclass=NullPool)

async_session_maker=async_sessionmaker(bind=engine,expire_on_commit=False)
async_session_maker_null_pool=async_sessionmaker(bind=engine_null_pool,expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Пример "сырого" запроса
# ===============================
# from sqlalchemy import text

# async def func():
#     async with engine.begin() as conn:
#         res =await conn.execute(text("SELECT version()"))
#         return print (res.fetchone())
#
# asyncio.run(func())
# =====================================