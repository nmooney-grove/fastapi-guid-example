"""Exercise the FastAPI app."""
from fastapi.testclient import TestClient

from fastapi_guid_example.app import app

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
