from typing import TypeVar, Generic

from pydantic import BaseModel

from src.database import Base

DBModelType = TypeVar("DBModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper(Generic[SchemaType, DBModelType]):
    db_model: type[DBModelType]
    schema: type[SchemaType]

    @classmethod
    def map_to_domain_entity(cls, data) -> SchemaType:
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data) -> DBModelType:
        return cls.db_model(**data.model_dump())
