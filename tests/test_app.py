"""Exercise the FastAPI app."""
# pylint: disable=redefined-outer-name
import uuid
from datetime import datetime

from fastapi.testclient import TestClient
import pytest

from fastapi_guid_example.app import app
from fastapi_guid_example.app import repo
from fastapi_guid_example.types import Entry


client = TestClient(app)


def test_create_guid():
    """It should create an Entry / GUID and return 201."""
    user =  "nate.k.mooney@gmail.com"
    expires = 12345
    data = {"user": user, "expires": expires}
    response = client.post("/guid", json=data)
    assert response.status_code == 201
    assert "guid" in response.json()
    assert response.json()["user"] == user
    assert response.json()["expires"] == expires


@pytest.fixture
@pytest.mark.asyncio
async def entry_in_db():
    """Fixture for an Entry in the db."""
    guid = uuid.uuid4()
    user =  "nate.k.mooney@gmail.com"
    # we exclude expires so we get the default date behavior
    entry_ = {"guid": guid, "user": user}
    # TODO the regular constructor should work just as well as from_dict
    entry = Entry.from_dict(entry_)
    val = await repo.add(entry)
    return val


@pytest.fixture
@pytest.mark.asyncio
async def expired_entry():
    """Fixture for an Entry in the db."""
    guid = uuid.uuid4()
    user = "nate.k.mooney@gmail.com"
    expires = 1
    entry_ = {"guid": guid, "user": user, "expires": expires}
    entry = Entry.from_dict(entry_)
    val = await repo.add(entry)
    return val


def test_update_guid(entry_in_db):
    """It should update an Entry / GUID and return 201."""
    entry = entry_in_db
    guid = entry.guid
    user = entry.user

    new_expires = 54321
    data = {"user": user, "expires": new_expires}
    response = client.post(f"/guid/{guid}", json=data)

    assert response.status_code == 201
    assert response.json()["guid"] == str(guid)
    assert response.json()["user"] == user
    assert response.json()["expires"] == new_expires


def test_get_guid_happy(entry_in_db):
    "It should return an a 200 reply and a GUID with its metadata."""
    entry = entry_in_db
    guid = entry.guid
    user = entry.user
    expires = entry.expires

    response = client.get(f"/guid/{guid}")

    assert response.status_code == 200
    assert response.json()["guid"] == str(guid)
    assert response.json()["user"] == user
    assert response.json()["expires"] == datetime.timestamp(expires)


def test_get_guid_does_not_exist():
    """It should return a 404."""
    guid = uuid.uuid4()

    response = client.get(f"/guid/{guid}")
    assert response.status_code == 404
    assert "guid" not in response.json()


def test_get_guid_expired(expired_entry):
    """It should return a 404."""
    entry = expired_entry
    guid = entry.guid

    response = client.get(f"/guid/{guid}")
    assert response.status_code == 404
    assert "guid" not in response.json()


def test_delete_entry(entry_in_db):
    """It should remove the entry, respond 204 and subsequent GET should 404."""
    entry = entry_in_db
    guid = entry.guid

    initial_response = client.delete(f"/guid/{guid}")
    assert initial_response.status_code == 204

    second_response = client.get(f"/guid/{guid}")
    assert second_response.status_code == 404
    assert "guid" not in second_response.json()
