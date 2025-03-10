# Presti AI API

A FastAPI-based REST API for Presti AI services, including image outpainting and more.

## Features

- FastAPI-based REST API
- Automatic API documentation (Swagger UI and ReDoc)
- Docker support
- Google Cloud Run ready
- Type-safe request/response models

## Local Development

1. Create a virtual environment:

```bash
python -m .venv venv
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

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Docker

Build the image:

```bash
docker build -t presti-ai-api .
```

Run the container:

```bash
docker run -p 8080:8080 presti-ai-api
```

## Deployment to Google Cloud Run

1. Build and push the container:

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/presti-ai-api
```

2. Deploy to Cloud Run:

```bash
gcloud run deploy presti-ai-api \
  --image gcr.io/YOUR_PROJECT_ID/presti-ai-api \
  --platform managed \
  --region YOUR_REGION \
  --allow-unauthenticated
```
