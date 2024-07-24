from app.main import app
from app.database import get_db
from app.utils.authentication import get_firebase_user_from_token
from fastapi.testclient import TestClient
import uuid

client = TestClient(app)

TEST_UID = uuid.UUID('06335e84-2872-4914-8c5d-3ed07d2a2f16').hex
TEST_ROADMAP_ID = 23
TEST_MODULE_ID = 33

async def override_get_firebase_user_from_token(q: str | None = None):
  return {
    "uid": TEST_UID,
    "provider_id": "firebase",
    "display_name": "Ricky Bobby", 
    "email": "test@neverbored.com", 
    "photo_url": None
  }


app.dependency_overrides[get_firebase_user_from_token] = override_get_firebase_user_from_token

def test_create_roadmap():
  bodyParams = {
    "description": "I want to learn React because I want to build website fast"
  }

  # Create roadmap
  response = client.post("/roadmaps", json=bodyParams)
  assert response.status_code == 200, response.text
  data = response.json()
  roadmap_id = data["id"]
  assert data["learning_goal"] == "I want to learn React because I want to build website fast"
  assert data["owner_id"], data["description"]
  assert len(data["modules"]) > 0

  # Ensure created roadmap is now followed by current user
  response = client.get("/roadmaps")
  assert response.status_code == 200, response.text
  data = response.json()
  created_roadmap = list(filter(lambda x: x["id"] == roadmap_id, data))[0]
  assert created_roadmap["learning_goal"] == "I want to learn React because I want to build website fast"
  assert created_roadmap["owner_id"], data["description"]

  # Ensure created roadmap can be retrieved
  response = client.get("/roadmaps/" + str(roadmap_id))
  assert response.status_code == 200, response.text
  data = response.json()
  assert data["learning_goal"] == "I want to learn React because I want to build website fast"
  assert data["owner_id"], data["description"]


# This is expensive to run... create a dummy response from tavily for testing before uncommenting.
# def test_populate_module():
#   response = client.post("/roadmaps/" + str(TEST_ROADMAP_ID) + "/modules/" + str(TEST_MODULE_ID) + "/populate")
#   assert response.status_code == 200, response.text
#   data = response.json()
#   assert len(data) > 0
#   assert data[0]["position_in_module"] == 0

#   response = client.get("modules/" + str(TEST_MODULE_ID))
#   assert response.status_code == 200, response.text
#   data = response.json()
#   assert data["submodules"][0]["position_in_module"] == 0

def test_get_module():
  response = client.get("/roadmaps/" + str(TEST_ROADMAP_ID) + "/modules/" + str(TEST_MODULE_ID))
  assert response.status_code == 200, response.text
  data = response.json()
  assert data["submodules"][0]["position_in_module"] == 0
  assert data["submodules"][0]["title"]
