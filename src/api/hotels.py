from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, PaginationDep
from src.schemas.hotels import HotelAdd, HotelPATCH

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    date_from: Annotated[date, Query(default="2026-09-15")],
    date_to: Annotated[date, Query(default="2026-09-20")],
    title: str | None = Query(None, description="Hotel name"),
    location: str | None = Query(None, description="Location"),
):
    per_page = pagination.per_page or 5

    return await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
    )


@router.get("/{hotel_date}")
@cache(expire=10)
async def get_hotel(hotel_id: int, db: DBDep):
    return await db.hotels.get_one_or_none(id=hotel_id)


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_date: Annotated[
        HotelAdd,
        Body(
            openapi_examples={
                "1": {
                    "summery": "Сочи",
                    "value": {
                        "title": "Отель Сочи 5 звезд",
                        "location": "У моря",
                    },
                },
                "2": {
                    "summery": "Дубай",
                    "value": {
                        "title": "Отель Дубай",
                        "location": "У фонтана",
                    },
                },
            }
        ),
    ],
):
    # ======================================
    # для дебага
    # print(add_hotel_stmt.compile( engine, compile_kwargs={"literal_binds": True}))
    # ========================
    hotel = await db.hotels.add(hotel_date)
    await db.commit()
    return {"status": "Ok", "data": hotel}


@router.put("/{hotel_id}")
async def edit_hotel(
    db: DBDep,
    hotel_id: int,
    hotel_date: HotelAdd,
):
    await db.hotels.edit(hotel_date, id=hotel_id)
    await db.commit()
    return {"status": "Ok"}


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле.",
    description="Частичное обновление",
)
async def partially_edit_hotel(
    db: DBDep,
    hotel_id: int,
    hotel_date: HotelPATCH,
):
    await db.hotels.edit(hotel_date, exclude_unset=True, id=hotel_id)
    await db.commit()

    return {"status": "Ok"}


@router.delete("/{hotel_id}")
async def delete_hotel(db: DBDep, hotel_id: int):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "Ok"}
