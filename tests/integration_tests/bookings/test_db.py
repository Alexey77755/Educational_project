from datetime import date

from src.schemas.bookings import BookingAdd


async def test_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(2021, 1, 10),
        date_to=date(2021, 2, 20),
        price=100,
    )

    new_booking = await db.bookings.add(booking_data)
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert booking
    assert booking.id == new_booking.id
    assert booking.room_id == new_booking.room_id
    assert booking.user_id == new_booking.user_id

    update_date = date(2021, 2, 10)
    booking_update_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(2021, 1, 20),
        date_to=update_date,
        price=100,
    )
    await db.bookings.edit(booking_update_data, id=new_booking.id)
    update_booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert update_booking
    assert update_booking.id == new_booking.id
    assert update_booking.date_to == update_date
    # await db.commit()

    await db.bookings.delete(id=new_booking.id)
    await db.commit()
