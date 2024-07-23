from fastapi.testclient import TestClient
from app.main import app
from app.utils.authentication import get_firebase_user_from_token


client = TestClient(app)

async def override_authentication_dependency(q: str | None = None):
    return {
        "uid": "1234",
        "provider_id": "firebase",
        "display_name": "Ricky Bobby", 
        "email": "test@neverbored.com", 
        "photo_url": None
    }

app.dependency_overrides[get_firebase_user_from_token] = override_authentication_dependency

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World!"}