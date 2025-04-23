# Presti AI API

A FastAPI-based REST API for Presti AI services, including image outpainting and more.

## Features

- FastAPI-based REST API
- PostgreSQL database support
- SQLAlchemy ORM
- Alembic for database migrations
- Automatic API documentation (Swagger UI and ReDoc)
- Docker support
- Google Cloud Run ready
- Type-safe request/response models

## Local Development

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the development server:

```bash
python main.py
```

The API will be available at http://localhost:8080

## API Documentation

- ReDoc: http://localhost:8080/redoc

## Alembic Migrations

1. Create a new migration:

```bash
alembic revision --autogenerate -m "migration_name"
```

2. Apply the migration:

```bash
alembic upgrade head
```

3. Downgrade the migration:

```bash
alembic downgrade -1
```

4. Show the current migration:

```bash
alembic current
```

5. Show the history of migrations:

```bash
alembic history
```

6. Show the status of migrations:

```bash
alembic status
```

## Docker

Build the image:

```bash
docker build -t presti-sdk .
```

Run the container:

```bash
docker run -p 8080:8080 presti-sdk
```

## Deployment to Google Cloud Run

1. Build and push the container:

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/presti-sdk
```

2. Deploy to Cloud Run:

```bash
gcloud run deploy presti-sdk \
  --image gcr.io/YOUR_PROJECT_ID/presti-sdk \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```
