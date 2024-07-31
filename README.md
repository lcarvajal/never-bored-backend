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
- Alemic
- Stripe

## Commands

- Change database host to @localhost:5432/never_bored
- Startup script: `./startup.sh`
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

### Migrations with Alemic

[Open documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

- `alembic revision --autogenerate -m "Initial migration"`
- `alembic upgrade head`

#### Alembic Autogenerate can not detect:

- Changes of table name. These will come out as an add/drop of two different
  tables, and should be hand-edited into a name change instead.
- Changes of column name. Like table name changes, these are detected as a
  column add/drop pair, which is not at all the same as a name change.
- Anonymously named constraints. Give your constraints a name, e.g.
  UniqueConstraint('col1', 'col2', name="my_name"). See the section The
  Importance of Naming Constraints for background on how to configure automatic
  naming schemes for constraints.
- Special SQLAlchemy types such as Enum when generated on a backend which
  doesn’t support ENUM directly - this because the representation of such a type
  in the non-supporting database, i.e. a CHAR+ CHECK constraint, could be any
  kind of CHAR+CHECK. For SQLAlchemy to determine that this is actually an ENUM
  would only be a guess, something that’s generally a bad idea. To implement
  your own “guessing” function here, use the
  sqlalchemy.events.DDLEvents.column_reflect() event to detect when a CHAR (or
  whatever the target type is) is reflected, and change it to an ENUM (or
  whatever type is desired) if it is known that that’s the intent of the type.
  The sqlalchemy.events.DDLEvents.after_parent_attach() can be used within the
  autogenerate process to intercept and un-attach unwanted CHECK constraints.
- Autogenerate can’t currently, but will eventually detect:

- Some free-standing constraint additions and removals may not be supported,
  including PRIMARY KEY, EXCLUDE, CHECK; these are not necessarily implemented
  within the autogenerate detection system and also may not be supported by the
  supporting SQLAlchemy dialect.
- Sequence additions, removals - not yet implemented.

## Generate local SSL

- `uvicorn app.main:app --host 0.0.0.0 --port 443 --ssl-keyfile=certs/key.pem --ssl-certfile=certs/cert.pem`

On macOS:

1. Open the Keychain Access application.
2. Go to File > Import Items and import the cert.pem file in System Keychain.
3. Find the certificate in the list, right-click on it, and select Get Info.
4. Expand the Trust section and select Always Trust for When using this
   certificate.
