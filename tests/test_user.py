from app.main import app
from app.database import get_db
from app.utils.authentication import get_firebase_user_from_token
from fastapi.testclient import TestClient
import uuid

client = TestClient(app)

TEST_UID = uuid.UUID('06335e84-2872-4914-8c5d-3ed07d2a2f16').hex
async def override_get_firebase_user_from_token(q: str | None = None):
  return {
    "uid": TEST_UID,
    "provider_id": "firebase",
    "display_name": "Ricky Bobby", 
    "email": "test@neverbored.com", 
    "photo_url": None
  }


app.dependency_overrides[get_firebase_user_from_token] = override_get_firebase_user_from_token

def test_create_user():
  test_user = {
    "uid": TEST_UID,
    "email": "test@neverbored.com",
    "name": "Ricky Bobby",
    "authentication_service": "firebase"
  }

  response = client.post("/users/", json=test_user)
  assert response.status_code == 200, response.text
  data = response.json()
  assert data["id"]
  assert data["name"] == "Ricky Bobby"
  assert data["email"] == "test@neverbored.com"
  assert uuid.UUID(data["uid"]).hex == test_user["uid"]
  assert data["authentication_service"] == "firebase"

  response = client.get("/users/" + str(data["id"]))
  assert response.status_code == 200, response.text
  data = response.json()
  assert data["name"] == "Ricky Bobby"
  assert data["email"] == "test@neverbored.com"
  assert uuid.UUID(data["uid"]).hex == test_user["uid"]
  assert data["authentication_service"] == "firebase"