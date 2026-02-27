import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from model.predictor import predict, load_model

app = FastAPI(title="Decision Tree Classifier API", version="1.0.0")


# ── Schemas ────────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    sepal_length: float = Field(..., example=5.1, description="Sepal length in cm")
    sepal_width:  float = Field(..., example=3.5, description="Sepal width in cm")
    petal_length: float = Field(..., example=1.4, description="Petal length in cm")
    petal_width:  float = Field(..., example=0.2, description="Petal width in cm")


class PredictResponse(BaseModel):
    predicted_class: int
    predicted_label: str
    probabilities:   dict[str, float]
    confidence:      float


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Decision Tree Classifier API — visit /docs"}


@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(body: PredictRequest):
    try:
        result = predict([
            body.sepal_length,
            body.sepal_width,
            body.petal_length,
            body.petal_width,
        ])
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info")
def model_info():
    try:
        _, meta = load_model()
        return meta
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/health")
def health():
    try:
        load_model()
        return {"status": "ok", "model_loaded": True}
    except Exception:
        return {"status": "degraded", "model_loaded": False}
