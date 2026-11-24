import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

sys.path.append(str(Path(__file__).parent.parent))

from fastapi.openapi.docs import get_swagger_ui_html

from src.api.auth import router as router_auth
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.api.hotels import router as router_hotels
from src.api.images import router as router_images
from src.api.rooms import router as router_rooms
from src.init import redis_manager

# async def send_email_bookings_today_checkin():
#     async for db in get_db():
#         bookings = await db.bookings.get_bookings_with_today_checkin()
#         print(f"{bookings}")
#
# async def run_send_email_regularly():
#     while True:
#         await send_email_bookings_today_checkin()
#         await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте ПРИЛОЖЕНИЯ
    # asyncio.create_task(run_send_email_regularly())
    await redis_manager.connect()

    FastAPICache.init(RedisBackend(redis_manager.get_client()), prefix="fastapi-cache")
    yield
    await redis_manager.close()
    # пРИ ВЫКЛЮЧЕНИИ/ПЕРЕЗАГРУЗКЕ ПРИЛОЖЕНИЯ


# app = FastAPI(lifespan=lifespan)

app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)
app.include_router(router_images)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    if app.openapi_url is None:
        raise RuntimeError("OpenAPI URL не настроен")

    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
