"""Exercise repository implementations."""
# pylint: disable=redefined-outer-name
from datetime import datetime
import uuid


import pytest

from fastapi_guid_example.types import Entry
from fastapi_guid_example.repository import SQLAlchemyRepository


@pytest.mark.asyncio
@pytest.fixture
async def sqlalchemy_repo():
    """Fixture for our SQL Alchemy Repo."""
    return SQLAlchemyRepository()


@pytest.mark.asyncio
async def test_get(sqlalchemy_repo):
    """It should add an entry to the store and return an entry without error."""
    entry_ = {
        "guid": uuid.uuid4(),
        "user": "nate.k.mooney@gmail.com",
        "expires": datetime.fromtimestamp(1545730073),
    }
    entry = Entry.from_dict(entry_)
    result = await sqlalchemy_repo.add(entry)
    # TODO actually query the DB to be sure it's there
    assert result == entry
