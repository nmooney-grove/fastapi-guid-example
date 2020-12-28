"""Repositories are abstractions over data access.

Here we define any repositories, associated data stores and access implementations.
"""
import abc
import os
from uuid import UUID

import databases
import sqlalchemy
import sqlalchemy_utils
import sqlite3

from .types import Entry

# TODO get this from env!
# DATABASE_URL = "postgresql://user:password@postgresserver/db"
DATABASE_URL = "sqlite:///./test.db"


class AbstractRepository(abc.ABC):
    """Define the methods of Repositories in general.

    This implementation is a little lazily constructed, it assumes our access patterns
    are always over Entries. This happens to be true at this time, but it's not as
    abstract as it claims to be.
    """

    @abc.abstractmethod
    async def get(self, guid: UUID) -> Entry:
        """How a repository returns a single Entry given its id."""
        ...

    @abc.abstractmethod
    async def delete(self, guid: UUID) -> None:
        """How a repository deletes an Entry given its id."""
        ...

    @abc.abstractmethod
    async def add(self, entry: Entry) -> Entry: 
        """How a repository adds an Entry to its backing data store."""
        ...

if os.getenv("TESTING"):
    TEST_DATABASE_URL = "sqlite:///./test.db"
    database = databases.Database(TEST_DATABASE_URL, force_rollback=True)
else:
    database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

entries = sqlalchemy.Table(
    "entries",
    metadata,
    sqlalchemy.Column("guid", sqlalchemy_utils.UUIDType, primary_key=True, unique=True),
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

    async def get(self, guid: UUID) -> Entry:
        """Query the DB for an Entry by id."""
        # TODO error handling!
        query = entries.select().where(entries.c.id == guid)
        val = await database.execute(query)
        return Entry.from_dict(val)

    async def delete(self, guid: UUID) -> None:
        """Delete an entry in the DB.

        THIS IS A DESTRUCTIVE OPERATION. There's no way to recover deleted data.
        We DO NOT use soft deletes.
        """
        query = sqlalchemy.delete(entries).where(entries.c.guid == guid)
        await database.execute(query)

    async def add(self, entry: Entry) -> Entry:
        """Add an Entry to the DB. Returning the Entry."""
        params = entry.dict()
        try:
            insert = sqlalchemy.insert(entries).values(params)
            await database.execute(insert)
        except (sqlalchemy.exc.IntegrityError, sqlite3.IntegrityError):
            # A mildly hackish way to language agnostically upsert, requires two passes
            # Okay, extra hacky given that we also need sqlite3-specific expections
            guid = params["guid"]
            new_params = {k: v for k,v in params.items() if k != "guid"}
            update = sqlalchemy.update(entries).where(entries.c.guid == guid).values(new_params)
            await database.execute(update)
        return Entry.from_dict(params)


initialize_repo = SQLAlchemyRepository