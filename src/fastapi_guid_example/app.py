import uuid
from datetime import datetime
from typing import Optional

import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel


class EntryIn(BaseModel):
    user: Optional[str]
    expires: Optional[int]


class Entry(BaseModel):
    guid: uuid.UUID
    user: str
    expires: datetime


app = FastAPI()


@app.on_event("startup")
async def startup():
    # TODO look at the right one!
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    # TODO look at the right one!
    await database.disconnect()


@app.post("/guid")
async def create_new_entry():
    # TODO generate new random GUID
    # TODO timestamp_out_30_days if no timestamp
    # TODO store it in the db with metadata
    # TODO store in cache (clobber)
    # TODO return all metadata + guid
    pass


@app.post("/guid/{guid}")
async def modify_entry(guid):
    # TODO store the metadata in the db
    # TODO timestamp_out_30_days if no timestamp
    # TODO the guid cannot be modified by this command
    # TODO store in cache (clobber)
    # TODO return all metadata + guid

    pass


@app.get("/guid/{guid}")
async def retrieve_entry(guid):

    # TODO check if it's in the cache
    # TODO read the entry from the db
    # TODO check if it's timestamp is valid
    # TODO if not return 404
    # TODO if not delete timestamp?
    # TODO return all metadata + guid
    pass


@app.delete("/guid/{guid}")
async def delete_entry(guid) -> None:
    # TODO remove the GUID and metadata from the db
    #
    pass
