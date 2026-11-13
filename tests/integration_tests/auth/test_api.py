import pytest


@pytest.mark.parametrize("email, password, status_code", [
    ("sobaka23@mail.ru", "sd2323", 200),
    ("sobaka23@mail.ru", "sd2323", 400),
    ("sobaka23mail.ru", "sd2323", 422),
    ("sobaka233@mail.ru", "sd2323", 200),
])
async def test_auth_flow(
        email: str,
        password: str,
        status_code: int,
    ac,

):
    response_register = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )

    assert response_register.status_code == status_code
    if status_code != 200:
        return

    response_login = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        }
    )

    assert response_login.status_code == status_code
    assert ac.cookies
    assert ac.cookies["access_token"]
    assert "access_token" in response_login.json()

    response_me = await ac.get("/auth/me")
    assert response_me.status_code == status_code
    data = response_me.json()
    assert data["email"] == email
    assert "id" in data
    assert "hashed_password" not in data
    assert "password" not in data
    # assert data["hashed_password"] == AuthService().get_password_hash(password)

    resp_loguot = await ac.post("/auth/logout")
    assert resp_loguot.status_code == status_code
    assert "access_token" not in ac.cookies
