import asyncio
import os
import sys
from asyncio import sleep
from typing import Any, Protocol, cast

from celery.result import AsyncResult
from celery.signals import worker_init
from PIL import Image

from src.database import async_session_maker_null_pool
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager

class CeleryTask(Protocol):
    """Интерфейс задачи: у неё есть .delay и .apply_async."""
    def delay(self, *args: Any, **kwargs: Any) -> AsyncResult:
        ...
    def apply_async(
        self,
        args: tuple | None = None,
        kwargs: dict | None = None,
        **options: Any,
    ) -> AsyncResult:
        ...

def as_celery_task(func: Any) -> CeleryTask:
    """Приводит объект декоратора @task к типизированному интерфейсу."""
    return cast(CeleryTask, func)

@worker_init.connect
def setup_event_loop(**kwargs):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@celery_instance.task
async def _test_task_impl():
    await sleep(5)
    print("Закончил")

test_task = as_celery_task(_test_task_impl)

@celery_instance.task
def _resize_image_impl(image_path: str):
    sizes = [1000, 100, 30]
    output_folder: str = "src/static/images"

    with Image.open(image_path) as img:
        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)

        if img.width <= 0:
            raise ValueError("Некорректная ширина исходного изображения")

        for size in sizes:
            # Сохраняем пропорции
            ratio = size / img.width
            height = max(1, int(img.height * ratio))

            resized = img.resize((size, height), Image.Resampling.LANCZOS)

            # Имя файла: исходное_имя_1000.jpg и т.д.
            new_file_name = f"{name}_{size}px{ext}.jpg"
            output_dir = os.path.join(output_folder, new_file_name)

            resized.save(
                output_dir,
                format="JPEG",
                optimize=True,
                progressive=True,
            )

        print(
            f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}"
        )

resize_image = as_celery_task(_resize_image_impl)

async def get_bookings_with_today_checkin_helper():
    print("начало")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_bookings_with_today_checkin()
        print(f"{bookings}")


@celery_instance.task(name="booking_today_checkin")
def _send_emails_to_users_with_today_checkin_impl():
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(get_bookings_with_today_checkin_helper())
    finally:
        loop.close()

