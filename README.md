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

- Change database host to @localhost:5432/never_bored
- `fastapi dev app/main.py`
- `pip freeze > requirements.txt`
- `pytest`

### Azure

- `az login`

### Docker

- Change database host to @postgres-db/never_bored
- `docker network create my_network`
- `docker run --detach --network my_network --name postgres-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=<xxx> -e POSTGRES_DB=never_bored -p 5434:5432 -d postgres`
- `docker build --tag never-bored-backend .`
- `docker run --detach --network my_network --publish 3100:8000 --env-file .env --name never-bored-backend never-bored-backend`
- Tag the FastAPI image for Azure
  `docker tag never-bored-backend neverbored.azurecr.io/never-bored-backend:latest`
- Push `docker push neverbored.azurecr.io/never-bored-backend:latest`

Helpers

- `docker images`
- `docker logs`
- `docker ps -a`
- Check running and exited containters `docker ps -a`
- `docker stop never-bored-backend`
- `docker rm never-bored-backend`

## Database

- `psql --host=neverboredserver.postgres.database.azure.com --port=5432 --username=myadmin  --dbname=postgres sslmode=require`
