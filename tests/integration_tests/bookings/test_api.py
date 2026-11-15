import pytest
import pytest_asyncio

from tests.conftest import get_db_null_pool


@pytest.mark.repeat(3)
@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, "2021-01-10", "2021-02-20", 200),
        (1, "2021-01-11", "2021-02-20", 200),
        (1, "2021-01-12", "2021-02-20", 200),
        (1, "2021-01-13", "2021-02-20", 200),
        (1, "2021-01-14", "2021-02-20", 200),
        (1, "2021-01-10", "2021-02-20", 409),
    ],
)
async def test_add_booking(room_id, date_from, date_to, status_code, authenticated_ac):
    response = await authenticated_ac.post(
        "/bookings/",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == status_code

    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "Ok"
        assert "data" in res


@pytest_asyncio.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null_pool():
        await _db.bookings.delete()
        await _db.commit()


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_quantity",
    [
        (1, "2021-01-10", "2021-02-20", 1),
        (1, "2021-01-10", "2021-02-20", 2),
        (1, "2021-01-10", "2021-02-20", 3),
    ],
)
async def test_add_and_get_my_bookings(
    room_id,
    date_from,
    date_to,
    status_quantity,
    authenticated_ac,
    delete_all_bookings,
):
    response = await authenticated_ac.post(
        "/bookings/",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == 200

    response = await authenticated_ac.get("/bookings/me")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == status_quantity
