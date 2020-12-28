"""Repositories are abstractions over data access.

Here we define any repositories, associated data stores and access implementations.
"""
import abc
from uuid import UUID

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
    """Define the methods of Repositories in general.

    This implementation is a little lazily constructed, it assumes our access patterns
    are always over Entries. This happens to be true at this time, but it's not as
    abstract as it claims to be.
    """

    @abc.abstractmethod
    async def get(self, id_: UUID) -> Entry:
        """How a repository returns a single Entry given its id."""
        ...

    @abc.abstractmethod
    async def delete(self, id_: UUID) -> None:
        """How a repository deletes an Entry given its id."""
        ...

    @abc.abstractmethod
    # TODO params should probably be a typed dict, no?
    async def add(self, params) -> Entry:  # TODO define the input data obj!!!
        """How a repository adds an Entry to its backing data store."""
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
    """SQL Alchemy Implementation of a backing data store.

    Our primary data store.
    """

    async def get(self, id_: UUID) -> Entry:
        """Query the DB for an Entry by id."""
        # TODO error handling!
        query = entries.select().where(entries.c.id == id_)
        val = await database.execute(query)
        return Entry.from_dict(val)

    async def delete(self, id_: UUID) -> None:
        """Delete an entry in the DB.

        THIS IS A DESTRUCTIVE OPERATION. There's no way to recover deleted data.
        We DO NOT use soft deletes.
        """
        query = entries.delete(None).where(entries.c.id == id_)
        # None param ^^^ is an artefact of https://github.com/sqlalchemy/sqlalchemy/issues/4656
        await database.execute(query)

    # TODO params should be an Entry
    async def add(self, params) -> Entry:
        """Add an Entry to the DB. Returning the Entry."""
        # TODO error handling
        # TODO ensure params is well formed
        query = entries.insert(None).values(params)
        # None param ^^^ is an artefact of https://github.com/sqlalchemy/sqlalchemy/issues/4656
        await database.execute(query)
        return Entry.from_dict(params)
