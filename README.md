# FCFS-List

FCFS-List is the backend API for a marketplace built around **waiting lists and first-come, first-served matching**. Buyers can register what they are looking for before an item is listed. When a seller offers a matching product, the intended experience is to connect interested buyers in queue order instead of making everyone compete to be first to click.

This repository contains the API and an admin interface; it does not include the marketplace's client application. The API is built with FastAPI, SQLModel/SQLAlchemy, and PostgreSQL, and runs in Docker.

## Marketplace features

- **Wishes:** buyers can save search keywords and refine a wish with brand, category, and area preferences.
- **Products:** sellers can list items for sale, loan, or either, with price, condition, size, status, and location/category information.
- **Ordered matches and offers:** matches connect a user and a product (optionally a wish); matches and offers have queue-order fields, statuses, and response deadlines.
- **Conversation and follow-through:** match messages, offers, transactions, and transaction messages support the steps from interest to a completed exchange.
- **Marketplace tools:** users can like and comment on products, and attach product images stored in Google Cloud Storage.
- **Authentication:** API access is protected by Auth0 scopes. Interactive API docs are available through Swagger UI.

### Matching implementation status

The data model and API support matches and queue ordering, but in the current code a match is created through the matches API; adding a wish or product does **not** automatically discover and create matches. Likewise, queue order is recorded and can be managed through the API, but automated advancement to the next buyer is not implemented here. The automatic matching experience described above is the product's intended differentiator, not a claim that this backend currently runs a matching job.

## Technology

- Python 3.10 (Docker image)
- FastAPI and Uvicorn
- PostgreSQL 13
- SQLModel / SQLAlchemy with Alembic migrations
- Auth0 authentication and Google Cloud Storage for image uploads
- Docker Compose for local development

## Run locally

### Prerequisites

- Docker Engine and Docker Compose (Compose v2 recommended)
- Auth0 API credentials/configuration for authenticated API requests
- A Google Cloud Storage bucket and application credentials if you plan to upload images

### Configure environment

Docker Compose reads variables from a root-level `.env` file. Start with the example and replace its placeholder values with your local configuration:

```sh
cp .env.example .env
```

Do not commit `.env` or credential files. The compose configuration uses these variables:

| Variable | Purpose |
| --- | --- |
| `DB_USERNAME` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_NAME` | PostgreSQL database name |
| `DB_PORT` | PostgreSQL port (normally `5432`) |
| `AUTH0_DOMAIN` | Auth0 tenant domain |
| `AUTH0_AUDIENCE` | Auth0 API audience |
| `AUTH0_RULE_NAMESPACE` | Auth0 rule/claim namespace passed to the API container |
| `GCS_BUCKET` | Google Cloud Storage bucket used for product images |
| `GOOGLE_APPLICATION_CREDENTIALS` | Host path to Google Cloud service-account credentials mounted into the container |
| `GCLOUD_PROJECT` | Google Cloud project ID |

Database and Auth0 configuration are needed to run and use the API. Google Cloud settings/credentials are needed for image upload and deletion. Keep local credentials private.

### Start the services

From the repository root, build and start the API and PostgreSQL:

```sh
docker compose up -d --build
```

The backend waits for PostgreSQL, applies Alembic migrations, and then starts Uvicorn on port `8000`.

- API welcome endpoint: <http://localhost:8000/>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Admin interface: <http://localhost:8000/admin/>

The versioned API routes are under `/v1` (for example, `/v1/products/` and `/v1/wishes/`). Use the Swagger UI to inspect request/response schemas and try endpoints with a valid Auth0 bearer token and the necessary scopes.

To follow service logs, use `docker compose logs -f backend`. Stop the services with `docker compose down`; the PostgreSQL data volume is retained. To remove the database volume as well, use `docker compose down -v` (this permanently deletes the local database data).

## API areas

The main resource groups are:

| Resource | Base route |
| --- | --- |
| Areas, brands, categories | `/v1/areas/`, `/v1/brands/`, `/v1/categories/` |
| Products and images | `/v1/products/`, `/v1/images` |
| Wishes and users | `/v1/wishes/`, `/v1/users/` |
| Matches and match messages | `/v1/matches/`, `/v1/matchmessages/` |
| Offers and transactions | `/v1/offers/`, `/v1/transactions/` |
| Product interaction | `/v1/likes/`, `/v1/comments/` |

The API uses Auth0 scopes such as `read:products`, `write:wishes`, and `modify:matches`; endpoint-level requirements are documented in Swagger UI.

## Development notes

- Alembic migrations run automatically when the backend container starts. Migration files are in `project/migrations/versions/`.
- Seed data and seeder utilities are under `project/app/seeders/`; they are not run automatically by the compose startup command.
- The dependency list is in `project/requirements.txt`.
- Automated test coverage and CI workflows are not currently included in this repository.
