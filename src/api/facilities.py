from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd
from src.tasks.tasks import test_task

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
@cache(expire=10)
async def get_All_facilities(db: DBDep):
    print("Иду в бд")
    return await db.facilities.get_all()


@router.post("/")
async def create_facilities(
        db: DBDep,
        facilities_date: Annotated[FacilityAdd, Body()],
):
    facility = await db.facilities.add(facilities_date)
    await db.commit()

    test_task.delay()

    return {"status": "Ok", "data": facility}
