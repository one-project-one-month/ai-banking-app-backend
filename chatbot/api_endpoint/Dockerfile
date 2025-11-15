FROM ubuntu:22.04

ENV PORT=5080
ENV MLFLOW_SERVER_WORKERS=10
ENV MLFLOW_TRACKING_URI_v1=https://dagshub.com/Ye-Bhone-Lin/ai-banking-app-backend.mlflow
ENV MLFLOW_EXPERIMENT_NAME=Refactor_Chatbot

ARG DAGSHUB_USER_TOKEN
ENV DAGSHUB_USER_TOKEN=${DAGSHUB_USER_TOKEN}

EXPOSE $PORT
EXPOSE ${MLFLOW_SERVER_PORT}

WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv \
    libgl1 libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv dagshub

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

RUN python3 -m nltk.downloader punkt punkt_tab
RUN pip install pydantic-core exceptiongroup

COPY ./chatbot/api_endpoint /app

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
