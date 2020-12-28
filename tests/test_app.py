"""Exercise the FastAPI app."""
import uuid

from fastapi.testclient import TestClient
import pytest

from fastapi_guid_example.app import app
from fastapi_guid_example.app import repo
from fastapi_guid_example.types import Entry


client = TestClient(app)

# TODO we gotta get to the test db somehow....

def test_create_guid():
    """It should create an Entry / GUID and return 200."""
    user =  "nate.k.mooney@gmail.com"
    expires = 12345
    data = {"user": user, "expires": expires}
    response = client.post("/guid", json=data)
    assert response.status_code == 200
    assert "guid" in response.json()
    assert response.json()["user"] == user
    assert response.json()["expires"] == expires

@pytest.fixture
@pytest.mark.asyncio
async def entry_in_db():
    """Fixture for an Entry in the db."""
    guid = uuid.uuid4()
    user =  "nate.k.mooney@gmail.com"
    expires = 12345
    entry_ = {"guid": guid, "user": user, "expires": expires}
    # TODO the regular constructor should work just as well as from_dict
    # ensure Entry already exists in the repo
    entry = Entry.from_dict(entry_)
    val = await repo.add(entry)
    return val

def test_update_guid(entry_in_db):
    """It should update an Entry / GUID and return 200."""
    entry = entry_in_db
    guid = entry.guid
    user = entry.user

    new_expires = 54321
    data = {"user": user, "expires": new_expires}
    response = client.post(f"/guid/{guid}", json=data)

    assert response.status_code == 200
    assert response.json()["guid"] == str(guid)
    assert response.json()["user"] == user
    assert response.json()["expires"] == new_expires
