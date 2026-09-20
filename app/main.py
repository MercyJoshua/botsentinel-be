import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .predictor import predictor
from .schemas import TrafficFlow, PredictionResponse


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("botsentinel")


app = FastAPI(
    title="BotSentinel API",
    description="Machine-learning-based botnet traffic detection API.",
    version="1.0.0",
)


frontend_url = os.getenv("FRONTEND_URL")

if not frontend_url:
    raise RuntimeError("FRONTEND_URL environment variable is not configured.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)


@app.get("/")
def root():
    return {
        "name": "BotSentinel API",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": "loaded",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_traffic(flow: TrafficFlow, request: Request):
    try:
        result = predictor.predict(flow.model_dump())

        logger.info(
            "Prediction completed | client=%s | prediction=%s | confidence=%.4f",
            request.client.host if request.client else "unknown",
            result["prediction"],
            result["confidence"],
        )

        return result

    except Exception:
        logger.exception("Prediction failed")

        raise HTTPException(
            status_code=500,
            detail="Prediction service temporarily unavailable.",
        )