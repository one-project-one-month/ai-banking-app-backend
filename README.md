# AI Banking App Backend

A collection of microservices and modules for AI-enabled banking features — OCR for identity documents, a chatbot FAQ service, and a real-time camera detection/authentication module.

This repository contains multiple self-contained services that can be run independently or containerized with Docker. Each module exposes REST (FastAPI) and / or gRPC endpoints and includes its own README with detailed usage.

## Table of contents

- [Modules](#modules)
- [Requirements](#requirements)
- [Quickstart — run locally](#quickstart---run-locally)
- [Docker](#docker)
- [Testing](#testing)
- [License](#license)

## Modules

- `licence_ocr/` — OCR service for license and passport images. FastAPI REST and gRPC interfaces. See `licence_ocr/README.md` for details and examples.
- `chatbot/` — FAQ/chatbot service that runs a lightweight Doc2Vec-based similarity search. FastAPI entrypoint and gRPC support. See `chatbot/README.md` for usage, environment variables and Dockerfile notes.
- `camera_detect/` — Real-time camera-based face pose detection and authentication module using MediaPipe and OpenCV. Contains a FastAPI server for integration. See `camera_detect/README.md`.

Each module has an `api_endpoint/` folder that contains the server code and Dockerfile where applicable.

## Requirements

- Python 3.10+ (project used Python 3.11 in some modules)
- Recommended: pipenv (Pipfile is present) or virtualenv + pip
- System dependencies: OpenCV, Tesseract OCR (for `licence_ocr`), and MediaPipe (for `camera_detect`) where applicable. See each module README for exact installation instructions.

Quick system package hints (macOS):

```bash
# Install Homebrew if needed: https://brew.sh/
brew install tesseract
pip install pipenv
```

## Quickstart — run locally

Choose the module you want to run and follow its README. Examples below assume you are in the repository root.

- licence_ocr (REST)

```bash
cd licence_ocr/api_endpoint/rest
pipenv install --dev
pipenv shell
uvicorn main:app --reload --port 5001
```

- chatbot (REST)

```bash
cd chatbot/api_endpoint
pipenv install --dev
pipenv shell
uvicorn main:app --host 0.0.0.0 --port 5080 --reload
```

- camera_detect (REST)

```bash
cd camera_detect/api_endpoint
pipenv install --dev
pipenv shell
uvicorn cam_api:app --host 0.0.0.0 --port 5006 --reload
```

Notes:
- Some modules include additional dependencies (e.g., `nltk` downloads for the chatbot). Follow module README instructions.
- For OCR features, ensure Tesseract binary is installed and available on PATH.

## Docker

Each module contains a Dockerfile under its `api_endpoint` directory. Build and run the module container from repo root.

Example: build and run the OCR service

```bash
docker build -f licence_ocr/api_endpoint/Dockerfile -t nrc-ocr .
docker run -p 5001:5000 nrc-ocr
```

Example: build and run the chatbot

```bash
docker build -f chatbot/api_endpoint/Dockerfile -t chatbot-api .
docker run -d --env-file .env -p 5080:5080 -p 5030:5030 chatbot-api
```

Adjust ports and environment variables as needed. See each module README for required env vars (for example: `DB_URI`, `MLFLOW_TRACKING_URI`, etc.).

## Testing

Unit tests are located in the `tests/` directory. You can run tests with the Python interpreter in a virtual environment.

```bash
pipenv install --dev
pipenv shell
pytest -q
```

Some modules include module-specific tests and notebooks. See `tests/test_ocr.py` for an example OCR unit test.

## License

This project repository includes code licensed under the project's license. Check individual module READMEs for more details.

