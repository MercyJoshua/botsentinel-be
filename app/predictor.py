from pathlib import Path

import pandas as pd
import joblib

from .preprocessing import normalize_features_dataframe


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "botsentinel_model.joblib"
)


class BotSentinelPredictor:
    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"BotSentinel model not found at: {model_path}"
            )

        self.model = joblib.load(model_path)

    def predict(self, flow: dict) -> dict:
        data = pd.DataFrame([flow])
        data = normalize_features_dataframe(data)

        prediction = int(self.model.predict(data)[0])

        probability = float(
            self.model.predict_proba(data)[0][1]
        )

        return {
            "prediction": "Botnet" if prediction == 1 else "Non-Botnet",
            "is_botnet": bool(prediction == 1),
            "botnet_probability": round(probability, 4),
            "confidence": round(
                probability if prediction == 1 else 1 - probability,
                4
            ),
        }


predictor = BotSentinelPredictor()