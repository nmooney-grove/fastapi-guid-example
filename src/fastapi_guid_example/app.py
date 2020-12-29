"""FastAPI Definition.

Here we describe routes, API data validation and HTTP error handling.
"""
import uuid
from datetime import datetime
from typing import Optional

import databases
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
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
database: databases.Database = repository.database

@app.on_event("startup")
async def startup():
    """Additional behaviors at FastAPI startup."""
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Additional behaviors at FastAPI shutdown."""
    await database.disconnect()


@app.post("/guid", status_code=status.HTTP_201_CREATED)
async def create_new_entry(entry_in: EntryIn):
    """CREATE endpoint for Entries / GUIDs."""
    entry = Entry.from_dict(entry_in.dict())
    result = await repo.add(entry)
    return result.dict(timestamp=True)


@app.get("/guid/{guid}")
async def retrieve_entry(guid):
    """READ endpoint for Entries / GUIDs."""
    result = await repo.get(guid)
    if result.is_valid():
        return result.dict(timestamp=True)
    raise HTTPException(status_code=404, detail="GUID not found or expired")

@app.post("/guid/{guid}", status_code=status.HTTP_201_CREATED)
async def modify_entry(guid, entry_in: EntryIn):
    """UPDATE endpoint for Entries / GUIDs."""
    entry_ = entry_in.dict()
    entry_["guid"] = guid
    entry = Entry.from_dict(entry_)
    result = await repo.add(entry)
    return result.dict(timestamp=True)


@app.delete("/guid/{guid}")
async def delete_entry(guid) -> None:
    """DELETE endpoint for Entries / GUIDs."""
    # TODO remove the GUID and metadata from the db
    guid += 1 # TODO JUNK
    return None
