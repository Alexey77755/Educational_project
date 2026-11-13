from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, UserIdDeep
from src.schemas.bookings import BookingAdd, BookingAddRequest

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
@cache(expire=10)
async def get_All_bokings(db: DBDep):
    return await db.bookings.get_all()


@router.get("/me")
@cache(expire=10)
async def get_me_bokings(db: DBDep, user_id: UserIdDeep):
    return await db.bookings.get_filtered(user_id=user_id)


@router.post("/")
async def create_booking(
        user_id: UserIdDeep,
        db: DBDep,
        booking_date: BookingAddRequest,
):
    # ======================================
    # для дебага
    # print(add_hotel_stmt.compile( engine, compile_kwargs={"literal_binds": True}))
    # ========================

    # rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)
    # query = (
    #     select(self.model)
    #     .options(joinedload(self.model.facilities))
    #     .filter(RoomsOrm.id.in_(rooms_ids_to_get))
    # )


    room = await db.rooms.get_one_or_none(id=booking_date.room_id)
    room_price: int = room.price
    _booking_data = BookingAdd(
        user_id=user_id,
        price=room_price,
        **booking_date.model_dump()
    )

    booking = await db.bookings.add_booking(_booking_data, hotel_id= room.hotel_id)
    await db.commit()
    return {"status": "Ok", "data": booking}
