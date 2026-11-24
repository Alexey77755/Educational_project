from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesORM
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Booking
from src.schemas.facilities import Facility
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room, RoomWithRels
from src.schemas.users import User


class HotelDataMapper(DataMapper[Hotel,HotelsOrm ]):
    db_model = HotelsOrm
    schema = Hotel


class RoomDataMapper(DataMapper[Room, RoomsOrm]):
    db_model = RoomsOrm
    schema = Room


class RoomDataWithRelsMapper(DataMapper[RoomWithRels, RoomsOrm]):
    db_model = RoomsOrm
    schema = RoomWithRels


class UserDataMapper(DataMapper[User,UsersOrm]):
    db_model = UsersOrm
    schema = User


class BookingDataMapper(DataMapper[Booking, BookingsOrm]):
    db_model = BookingsOrm
    schema = Booking


class FacilityDataMapper(DataMapper[Facility, FacilitiesORM]):
    db_model = FacilitiesORM
    schema = Facility
