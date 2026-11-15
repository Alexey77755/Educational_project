from datetime import datetime, timedelta

import bcrypt
import jwt
from dateutil.tz import UTC
from fastapi import HTTPException
from starlette import status

from src.config import settings


class AuthService:
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def get_password_hash(self, password: str) -> str:
        # bcrypt работает только с байтами
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def decode_jwt_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.exceptions.DecodeError:
            print(token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Не верный токен"
            )
