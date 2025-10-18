FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PORT=5006
EXPOSE $PORT

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    libgl1 libglib2.0-0 tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv

RUN pipenv requirements --categories "default" > requirements.txt && \
    pip install --no-cache-dir --default-timeout=120 --retries=10 -r requirements.txt

RUN pip install --no-cache-dir pydantic-core exceptiongroup

COPY ./camera_detect/api_endpoint /app

CMD ["uvicorn", "cam_api:app", "--host", "0.0.0.0", "--port", "5006"]
