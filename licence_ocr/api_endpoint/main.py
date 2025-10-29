"""API endpoint for OCR processing of licences and passports."""

import os
import shutil
import uuid
from contextlib import asynccontextmanager
from typing import Literal

import sentry_sdk
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from utils import model_ocr
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

load_dotenv()

ocr_model = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the OCR model on startup and clean up on shutdown."""
    ocr_model_worker = model_ocr.OCR_Model()
    ocr_model["OCR_Model"] = ocr_model_worker
    yield
    ocr_model.clear()


app = FastAPI(lifespan=lifespan)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True,
)


@app.post("/ocr")
def ocr_endpoint(
    file: UploadFile = File(...), class_name: Literal["passport", "licence"] = Form(...)
):
    """Endpoint to handle OCR requests."""
    try:
        temp_file = f"temp_{uuid.uuid4()}.jpg"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ocr = ocr_model["OCR_Model"]
        ocr.image_path = temp_file

        with sentry_sdk.start_transaction(op="task", name=f"OCR-{class_name}"):
            if class_name == "passport":
                with sentry_sdk.start_span(
                    op="preprocess", description="Preprocess Passport"
                ):
                    gray = ocr.preprocess_image_for_passport_ocr()

                with sentry_sdk.start_span(
                    op="model", description="Passport OCR Model"
                ):
                    result = ocr.passport_ocr_model(gray)
                    os.remove(temp_file)

            elif class_name == "licence":
                with sentry_sdk.start_span(
                    op="preprocess", description="Preprocess Licence"
                ):
                    gray = ocr.preprocess_image_for_licence_ocr()

                with sentry_sdk.start_span(op="model", description="Licence OCR Model"):
                    result = ocr.licence_ocr_model(gray)
                    os.remove(temp_file)

        return {"data": result}

    except Exception as e:
        sentry_sdk.capture_exception(e)  # send detailed error to Sentry
        raise HTTPException(status_code=500, detail="OCR processing failed")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
