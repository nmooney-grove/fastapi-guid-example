import abc
from uuid import UUID
from typing import Any
from datetime import datetime

import asyncio
import aioredis
import databases
import sqlalchemy
import sqlalchemy_utils

from .types import Entry

# TODO get this from env!
# DATABASE_URL = "postgresql://user:password@postgresserver/db"
# if TESTING:
DATABASE_URL = "sqlite:///./test.db"

REDIS_URL = "redis://localhost"


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self, id_: UUID) -> Entry:
        ...

    @abc.abstractmethod
    async def delete(self, id_: UUID) -> None:
        ...

    @abc.abstractmethod
    # TODO params should probably be a typed dict, no?
    async def add(self, params) -> Entry:  # TODO define the inpute data obj!!!
        ...


database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

entries = sqlalchemy.Table(
    "entries",
    metadata,
    sqlalchemy.Column("id_", sqlalchemy_utils.UUIDType, primary_key=True, unique=True),
    sqlalchemy.Column("user", sqlalchemy.String),
    sqlalchemy.Column("expires", sqlalchemy.DateTime),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class SQLAlchemyRepository(AbstractRepository):
    async def get(self, id_: UUID) -> Entry:
        # TODO error handling!
        query = entries.select().where(entries.c.id == id_)
        val = await database.execute(query)
        return Entry.from_dict(val)

    async def delete(self, id_: UUID) -> None:
        query = entries.delete(None).where(entries.c.id == id_)
        # None param ^^^ is an artefact of https://github.com/sqlalchemy/sqlalchemy/issues/4656
        await database.execute(query)

    # TODO params should be an Entry
    async def add(self, params) -> Entry:
        # TODO error handling
        # TODO ensure params is well formed
        query = entries.insert(None).values(params)
        # None param ^^^ is an artefact of https://github.com/sqlalchemy/sqlalchemy/issues/4656
        await database.execute(query)
        return Entry.from_dict(params)


class RedisRepository(AbstractRepository):
    def __init__(self, settings):
        self.settings = settings

    async def _init(self, url):
        self.redis = await aioredis.create_redis_pool(url)

    async def get(self, id_: UUID) -> Entry:
        # TODO handle absent redis
        # TODO this encoding might be right, but the object is wrong!
        val = await self.redis.get(id_, encoding="utf-8")
        return Entry.from_dict(val)

    async def delete(self, id_: UUID) -> None:
        # TODO handle absent redis
        await self.redis.delete(id_)

    async def add(self, params) -> Entry:
        # TODO handle absent redis
        # TODO ensure params is well formed
        id_ = params.get("id_")
        await self.redis.set(id_, params)
        return Entry.from_dict(params)


# TODO tear down methods
# redis.close()
# await redis.wait_closed()


async def create_redis_repository(url: str, settings) -> RedisRepository:
    repo = RedisRepository(settings)
    await repo._init(url)
    return repo
