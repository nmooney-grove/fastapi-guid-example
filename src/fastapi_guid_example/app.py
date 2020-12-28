"""FastAPI Definition.

Here we describe routes, API data validation and HTTP error handling.
"""
import uuid
from datetime import datetime
from typing import Optional

import databases
from fastapi import FastAPI
from pydantic import BaseModel

from . import repository
from .types import Entry


class EntryIn(BaseModel):
    """Minimum data for Entry requests."""

    user: Optional[str]
    expires: Optional[int]


class EntryOut(BaseModel):
    """Return type for Entry endpoints."""

    guid: uuid.UUID
    user: str
    expires: datetime


app = FastAPI()
repo: repository.AbstractRepository = repository.initialize_repo()
database = repository.database

@app.on_event("startup")
async def startup():
    """Additional behaviors at FastAPI startup."""
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Additional behaviors at FastAPI shutdown."""
    await database.disconnect()


@app.post("/guid")
async def create_new_entry(entry_in: EntryIn):
    """CREATE endpoint for Entries / GUIDs."""
    entry = Entry.from_dict(entry_in.dict())
    result = await repo.add(entry)
    return result.dict(timestamp=True)


@app.get("/guid/{guid}")
async def retrieve_entry(guid):
    """READ endpoint for Entries / GUIDs."""
    # TODO check if it's in the cache
    # TODO read the entry from the db
    # TODO check if it's timestamp is valid
    # TODO if not return 404
    # TODO if not delete timestamp?
    # TODO return all metadata + guid
    return guid


@app.post("/guid/{guid}")
async def modify_entry(guid):
    """UPDATE endpoint for Entries / GUIDs."""
    # TODO store the metadata in the db
    # TODO the guid cannot be modified by this command
    # TODO store in cache (clobber)
    # TODO return all metadata + guid
    return guid


@app.delete("/guid/{guid}")
async def delete_entry(guid) -> None:
    """DELETE endpoint for Entries / GUIDs."""
    # TODO remove the GUID and metadata from the db
    guid += 1 # TODO JUNK
    return None
