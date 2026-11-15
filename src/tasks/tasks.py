import asyncio
import os
import sys
from asyncio import sleep

from celery.signals import worker_init
from PIL import Image

from src.database import async_session_maker_null_pool
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager


@worker_init.connect
def setup_event_loop(**kwargs):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@celery_instance.task
def test_task():
    sleep(5)
    print("Закончил")


@celery_instance.task
def resize_image(image_path: str):
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


async def get_bookings_with_today_checkin_helper():
    print("начало")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_bookings_with_today_checkin()
        print(f"{bookings}")


@celery_instance.task(name="booking_today_checkin")
def sen_emails_to_users_with_today_checkin():
    asyncio.run(get_bookings_with_today_checkin_helper())
