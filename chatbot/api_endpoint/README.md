# Chatbot API (RefactorModel)

This service exposes REST API for querying a RefactorModel that uses stored FAQ data to retrieve and return the best matching answer.

## Overview

- Framework: FastAPI
- Entrypoint: `main.py` (runs with Uvicorn)
- Primary endpoint: POST `/queryRequest`
- Purpose: Accept a SQL-like user query in JSON, run a similarity search against FAQs stored in the database and return the best-matched answer or a helpful message.

## Contract

- Endpoint: POST /queryRequest
- Content-Type: application/json
- Request JSON schema (`textRequest`):

  {
    "SQL_QUERY": "<user question text>"
  }

- Success (200): returns the model output as plain text (string) — the selected answer from the FAQ database.
- Error (200 with error body): The current implementation logs the exception to MLflow and returns {"Error Occured"}.

Note: The API currently returns success status codes even on internal errors; see the Error Handling section for details and recommended improvement.

## Example Request

curl example:

```bash
curl -X POST http://localhost:5008/queryRequest \
  -H "Content-Type: application/json" \
  -d '{"SQL_QUERY": "How do I reset my password?"}'
```

Example JSON body:

{
  "SQL_QUERY": "How do I reset my password?"
}

Expected successful response (example):

"To reset your password, visit the account settings page and click 'Reset Password'..."

Or, when the similarity score is below threshold:

"There is no exact answer for that question"

## Environment Variables

The service relies on the following environment variables (set in the container or host environment):

- DB_URI: PostgreSQL connection string used by `db_access.RetrieveData.connect()` (e.g. `postgresql://user:pass@host:5432/dbname`)
- MLFLOW_TRACKING_URI: MLflow tracking server URI (optional, used to log runs). The `main.py` calls `mlflow.set_tracking_uri(...)` and `mlflow.set_experiment(...)`.
- MLFLOW_EXPERIMENT_NAME: Name of the MLflow experiment.

Dockerfile also sets defaults used when running the service via Dockerfile in `chatbot/api_endpoint/Dockerfile`.

## How it works

1. The API receives a JSON object with `SQL_QUERY`.
2. A `RetrieveData` instance connects to the DB and fetches all `question` and `answer` rows from table `faq`.
3. The code zips questions and answers into a dictionary, tokenizes questions with NLTK, trains an in-memory Doc2Vec model on the dataset, and infers a vector from the user input.
4. The model selects the most similar document. If the similarity score is above a threshold (0.8), the corresponding answer is returned. Otherwise a fallback message is returned.
5. MLflow is used to log input and output and any exception traces.

## Running locally (development)

Prerequisites:

- Python 3.10+ (the Dockerfile uses Ubuntu and python3)
- PostgreSQL (or accessible `DB_URI` pointing to a running DB with an `faq` table)
- Pipenv or pip with the dependencies listed in `Pipfile`.

Steps:

1. Install dependencies (using pipenv from the repo root or inside `chatbot/api_endpoint`):

```bash
pipenv install --dev
pipenv shell
python -m nltk.downloader punkt
```

2. Export env vars (example):

```bash
export DB_URI="postgresql://user:pass@host:5432/dbname"
export MLFLOW_TRACKING_URI="http://localhost:5030"
export MLFLOW_EXPERIMENT_NAME="Refactor_Chatbot"
export GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

3. Run the API:

```bash
uvicorn main:app --host 0.0.0.0 --port 5080 --reload
```

```bash
mlflow ui  --host 127.0.0.1 --port 5030 --backend-store-uri sqlite:///mlruns.sqlite
```

Mlflow server will be running on 
```bash 
http://127.0.0.1:5030
```


FastAPI Server will be running on 
```bash 
http://127.0.0.1:5080
```

4. Test the endpoint with curl or Postman (see Example Request above).

## Running with Docker

There is a `Dockerfile` under `chatbot/api_endpoint` that installs dependencies and runs both an MLflow server and the Uvicorn app together. To build and run the image manually:

```bash
docker build -t chatbot-api -f chatbot/api_endpoint/Dockerfile .
docker run -d --env-file .env -p 5080:5080 -p 5030:5030 chatbot
```

Notes:

- The Dockerfile in this repo starts an MLflow server in the container and the FastAPI app. It exposes port `5080` for the app and `5030` for MLflow by default (see Dockerfile environment variables). The `docker run` command above maps host ports to these internal ports.

## Error handling and improvements

- Current behavior: exceptions are caught in `main.request_text`, logged to MLflow (as `error_type`), and the API returns `{"Error Occured"}` with HTTP 200. This is not ideal.
- Recommended improvements:
  - Return proper error status codes (e.g. 500) on unexpected exceptions.
  - Improve response schema to consistently return JSON with keys like `success`, `data`, `error`.
  - Avoid training Doc2Vec on every request; instead train offline and load a pre-trained model for inference to improve latency.
  - Limit NLTK downloads in the Docker build to avoid runtime downloads.

## Contract (mini)

- Inputs: JSON with `SQL_QUERY` string.
- Outputs: string answer or a fallback message.
- Error modes: DB connection failures, empty DB, NLP model training errors, MLflow unavailability.

## Edge cases

- Empty or missing `SQL_QUERY`: The code does not explicitly validate this. A missing field will cause Pydantic validation to fail and a 422 response from FastAPI. Consider validating empty strings and returning a 400 with a helpful message.
- Very large inputs: May increase Doc2Vec inference time; consider truncating or rate-limiting requests.
- DB empty: `retrieve_questions()` will return an empty list and training will fail — handle this case by returning a clear message and HTTP 204/400.


## Files of interest

- `main.py` - FastAPI app and endpoint
- `db_access.py` - database retrieval, Doc2Vec training and inference
- `model_work.py` - model wrapper used by the API
- `schema.py` - Pydantic request schema
- `Dockerfile` - container image for chatbot API + mlflow server

---
