from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatch, RoomPatchRequest

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_date}/Rooms")
@cache(expire=10)
async def get_rooms(
        db: DBDep,
        hotel_id: int,
        date_from: Annotated[date, Query(examples=["2026-09-15"])],
        date_to: Annotated[date, Query(examples=["2026-09-20"])],
):
    return await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


@router.get("/{hotel_id}/Rooms/{room_id}")
@cache(expire=10)
async def get_room(db: DBDep,
                   hotel_id: int,
                   room_id: int):
    return await db.rooms.get_one_or_none_with_rels(hotel_id=hotel_id, id=room_id)


@router.post("/{hotel_id}/Rooms")
async def create_rooms(db: DBDep,
                       hotel_id: int,
                       room_date: Annotated[RoomAddRequest, Body()]
                       ):
    data = RoomAdd(hotel_id=hotel_id, **room_date.model_dump())

    # ======================================
    # для дебага
    # print(add_hotel_stmt.compile( engine, compile_kwargs={"literal_binds": True}))
    # ========================
    room = await db.rooms.add(data)

    rooms_facilities_data = [RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_date.facilities_ids]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()
    return {"status": "Ok", "data": room}


@router.put("/{hotel_id}/Rooms/{room_id}")
async def edit_rooms(db: DBDep,
                     hotel_id: int,
                     room_id: int,
                     room_date: RoomAddRequest,
                     ):
    data = RoomAdd(hotel_id=hotel_id, **room_date.model_dump())
    await db.rooms.edit(data, hotel_id=hotel_id, id=room_id)

    await db.rooms_facilities.set_room_facilities(room_id, facilities_ids=room_date.facilities_ids)
    await db.commit()
    return {"status": "Ok"}


@router.patch("/{hotel_id}/Rooms/{room_id}")
async def partially_edit_rooms(
        db: DBDep,
        hotel_id: int,
        room_id: int,
        room_date: RoomPatchRequest,
):
    _room_data_dict = room_date.model_dump(exclude_unset=True)
    data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)

    await db.rooms.edit(data, exclude_unset=True, hotel_id=hotel_id, id=room_id)

    if "facilities_ids" in _room_data_dict:
        await db.rooms_facilities.set_room_facilities(room_id, facilities_ids=_room_data_dict["facilities_ids"])

    await db.commit()

    return {"status": "Ok"}


@router.delete("/{hotel_id}/Rooms/{room_id}")
async def delete_rooms(
        db: DBDep,
        hotel_id: int,
        room_id: int,
):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()
    return {"status": "Ok"}
