from datetime import date

from sqlalchemy import delete, select, update
from sqlalchemy.orm import joinedload

from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from src.repositories.utils import rooms_ids_for_booking


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(self, hotel_id, date_from: date, date_to: date):

        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)
        # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        # RoomsOrm.id.in_(rooms_ids_to_get)

        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )
        result = await self.session.execute(query)
        return [
            RoomDataWithRelsMapper.map_to_domain_entity(model)
            for model in result.unique().scalars().all()
        ]

    async def get_one_or_none_with_rels(self, **filter_by):
        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter_by(**filter_by)
        )
        model = await self.session.execute(query)
        model = model.unique().scalars().one_or_none()
        if model is None:
            return None
        return RoomDataWithRelsMapper.map_to_domain_entity(model)

    async def edit(self, data: model, exclude_unset: bool = False, **filter_by) -> None:

        room_id = filter_by.get("id")
        if await self.check(hotel_id=data.hotel_id, id=room_id):
            update_hotel_stmt = (
                update(self.model)
                .filter_by(**filter_by)
                .values(**data.model_dump(exclude_unset=exclude_unset))
            )
            await self.session.execute(update_hotel_stmt)

    async def delete(self, **filter_by) -> None:
        room_id = filter_by.get("id")
        hotel_id = filter_by.get("hotel_id")
        if await self.check(id=room_id, hotel_id=hotel_id):
            delete_hotel_stmt = delete(self.model).filter_by(**filter_by)
            await self.session.execute(delete_hotel_stmt)
