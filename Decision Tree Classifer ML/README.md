# Decision Tree Classifier — FastAPI + Gradio

ML pipeline with a trained Decision Tree on the Iris dataset,
a FastAPI prediction API, and a Gradio interactive UI.

## Structure

```
dt-classifier/
├── model/
│   ├── train.py       # Train & save the model
│   └── predictor.py   # Load model + predict helper
├── api/
│   └── main.py        # FastAPI: /predict, /model/info, /health
├── ui/
│   └── app.py         # Gradio UI (calls FastAPI)
└── requirements.txt
```

## Setup & Run

```bash
pip install -r requirements.txt

# Step 1 — Train the model (creates model/model.pkl)
python model/train.py

# Step 2 — Start FastAPI (terminal 1)
uvicorn api.main:app --reload --port 8000

# Step 3 — Start Gradio (terminal 2)
python ui/app.py
```

- **Gradio UI** → http://localhost:7860
- **FastAPI docs** → http://localhost:8000/docs

## API

### POST /predict
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```
Response:
```json
{
  "predicted_class": 0,
  "predicted_label": "setosa",
  "probabilities": { "setosa": 1.0, "versicolor": 0.0, "virginica": 0.0 },
  "confidence": 1.0
}
```

### GET /model/info
Returns accuracy, depth, feature importances, train/test split info.

### GET /health
Returns model load status.
