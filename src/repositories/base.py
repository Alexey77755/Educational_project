from typing import TypeVar, Generic

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import MultipleResultsFound

from src.database import Base
from src.repositories.mappers.base import DataMapper
from utils.db_manager import DBManager

SchemaType = TypeVar("SchemaType", bound=BaseModel)
DBModelType = TypeVar("DBModelType", bound=Base)

class BaseRepository(Generic[SchemaType, DBModelType]):
    model : type[DBModelType]
    mapper: type[DataMapper[SchemaType, DBModelType]]

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        model = await self.session.execute(query)
        model = model.scalars().one_or_none()
        if model is None:
            raise HTTPException(status_code=404, detail="Model not found")
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        add_data_stmt = (
            insert(self.model).values(**data.model_dump()).returning(self.model)
        )
        # try:
        result = await self.session.execute(add_data_stmt)
        model = result.scalars().one()
        return self.mapper.map_to_domain_entity(model)
        # except IntegrityError as e:
        #     await self.session.rollback()
        #
        #     error_msg = str(e.orig).lower()
        #     if "email" in error_msg:
        #         raise HTTPException(
        #             status_code=409,
        #             detail="Пользователь с таким email уже существует"
        #         )
        #     raise HTTPException(status_code=409, detail=f"Ошибка: {e.detail}")

    async def add_bulk(self, data: list[SchemaType]):
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        # try:
        await self.session.execute(add_data_stmt)

        # except IntegrityError as e:
        #     await self.session.rollback()
        #
        #     error_msg = str(e.orig).lower()
        #     if "email" in error_msg:
        #         raise HTTPException(
        #             status_code=409,
        #             detail="Пользователь с таким email уже существует"
        #         )
        #     raise HTTPException(status_code=409, detail=f"Ошибка: {e.detail}")

    async def check(self, **filter_by):
        try:
            result = await self.get_one_or_none(**filter_by)
            if result is None:
                raise HTTPException(
                    status_code=404, detail=f"Отель с id={filter_by} не найден"
                )

        except MultipleResultsFound:
            raise HTTPException(
                status_code=400, detail=f"Отель с id={filter_by} не найден"
            )

        return True

    async def edit(
        self, data: BaseModel, exclude_unset: bool = False, **filter_by
    ) -> None:
        hotel_id = filter_by.get("id")
        if await self.check(id=hotel_id):
            update_hotel_stmt = (
                update(self.model)
                .filter_by(**filter_by)
                .values(**data.model_dump(exclude_unset=exclude_unset))
            )
            await self.session.execute(update_hotel_stmt)

    async def delete(self, **filter_by) -> None:
        hotel_id = filter_by.get("id")
        if await self.check(id=hotel_id):
            delete_hotel_stmt = delete(self.model).filter_by(**filter_by)
            await self.session.execute(delete_hotel_stmt)
