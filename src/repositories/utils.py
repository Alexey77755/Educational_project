from datetime import date

from sqlalchemy import func, select

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm


def rooms_ids_for_booking(date_from: date, date_to: date, hotel_id: int | None = None):
    rooms_count = (
        select(BookingsOrm.room_id, func.count("*").label("room_booked"))
        .select_from(BookingsOrm)
        .where(
            BookingsOrm.date_from <= date_to,
            BookingsOrm.date_to >= date_from,
        )
        .group_by(BookingsOrm.room_id)
        .cte(name="rooms_count")
    )
    occupied_rooms = (
        select(
            RoomsOrm.id.label("room_id"),
            (RoomsOrm.quantity - func.coalesce(rooms_count.c.room_booked, 0)).label(
                "quantity_free_rooms"
            ),
        )
        .select_from(RoomsOrm)
        .outerjoin(rooms_count, RoomsOrm.id == rooms_count.c.room_id)
        .cte(name="occupied_rooms")
    )

    rooms_ids_for_hotel = select(RoomsOrm.id).select_from(RoomsOrm)

    if hotel_id is not None:
        rooms_ids_for_hotel = rooms_ids_for_hotel.where(RoomsOrm.hotel_id == hotel_id)

    rooms_ids_to_get = (
        select(occupied_rooms.c.room_id)
        .select_from(occupied_rooms)
        .where(
            occupied_rooms.c.quantity_free_rooms > 0,
            occupied_rooms.c.room_id.in_(rooms_ids_for_hotel),
        )
    )

    return rooms_ids_to_get
