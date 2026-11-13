async def test_get_hotels(ac):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": "2021-01-10",
            "date_to": "2021-02-20",
        })
    print(f"{response.json()=}")

    assert response.status_code == 200


async def test_add_facilities(ac):
    facility_title="WI-FI"
    insert_data = await ac.post(
        "/facilities/",
        json={
            "title": facility_title,
        },
    )


    assert insert_data.status_code == 200
    res = insert_data.json()
    assert isinstance(res,dict)
    assert res["data"]["title"] == facility_title
    assert "data" in res

async def test_get_facilities(ac):
    response = await ac.get("/facilities")
    assert response.status_code == 200
    assert isinstance(response.json(),list)