FROM ubuntu:22.04

ENV PORT=5080
ENV MLFLOW_SERVER_HOST=0.0.0.0
ENV MLFLOW_SERVER_PORT=5030
ENV MLFLOW_SERVER_WORKERS=10
ENV MLFLOW_TRACKING_URI=http://localhost:5030
ENV MLFLOW_EXPERIMENT_NAME=Refactor_Chatbot
ENV HF_TOKEN=${HF_TOKEN}

EXPOSE $PORT
EXPOSE ${MLFLOW_SERVER_PORT}

WORKDIR /app

RUN apt-get update && apt-get install -y python3  python3-pip python3-venv\
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

RUN python3 -m nltk.downloader punkt punkt_tab

RUN pip install pydantic-core exceptiongroup

COPY ./chatbot/api_endpoint /app

CMD ["sh", "-c", "mlflow server --host 0.0.0.0 --port ${MLFLOW_SERVER_PORT} --backend-store-uri sqlite:///mlflow.db & uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
