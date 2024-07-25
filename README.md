# Never Bored Learning Backend

The backend for the Never Bored Learning Frontend.

## API Docs

[Open docs](http://127.0.0.1:8000/docs)

## Techologies

- FastAPI
- Firebase Authentication and Messaging
- Posthog
- Langchain
- Tavily search
- SQLalchemy
- Pytest

## Commands

- `fastapi dev app/main.py`
- `pip freeze > requirements.txt`
- `pytest`

### Docker
- `docker images`
- `docker logs`
- `docker ps -a`
- Check running and exited containters `docker ps -a`
- `docker build --tag never-bored-backend .`
- `docker run --detach --publish 3100:3100 --env-file .env never-bored-backend`