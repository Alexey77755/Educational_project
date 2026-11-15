from sqlalchemy import delete, insert, select

from src.models.facilities import FacilitiesORM, RoomsFacilitiesORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FacilityDataMapper


class FacilitiesRepository(BaseRepository):
    model = FacilitiesORM
    mapper = FacilityDataMapper


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesORM
    mapper = FacilityDataMapper

    async def set_room_facilities(
        self, room_id: int, facilities_ids: list[int]
    ) -> None:

        facility_ids_for_room = (
            select(self.model.facility_id)
            .select_from(self.model)
            .where(self.model.room_id == room_id)
        )

        facility_base = await self.session.execute(facility_ids_for_room)
        facility_base: list[int] = facility_base.scalars().all()

        facilities_for_append: list[int] = list(
            set(facilities_ids) - set(facility_base)
        )

        if facilities_for_append:
            edit_data_stmt = insert(self.model).values(
                [
                    {"room_id": room_id, "facility_id": f_id}
                    for f_id in facilities_for_append
                ]
            )
            await self.session.execute(edit_data_stmt)

        facilities_for_delete: list[int] = list(
            set(facility_base) - set(facilities_ids)
        )

        if facilities_for_delete:
            delete_data_stmt = delete(self.model).where(
                self.model.room_id == room_id,
                self.model.facility_id.in_(facilities_for_delete),
            )
            await self.session.execute(delete_data_stmt)
