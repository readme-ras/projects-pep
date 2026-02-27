"""
Gradio frontend for the Decision Tree Classifier.
Calls the FastAPI backend at FASTAPI_URL.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from sklearn.tree import export_text
from model.predictor import load_model

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

FLOWER_EMOJI = {"setosa": "🌸", "versicolor": "🌺", "virginica": "🌼"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_prob_chart(probabilities: dict) -> go.Figure:
    labels  = list(probabilities.keys())
    values  = list(probabilities.values())
    colors  = ["#6366f1", "#f59e0b", "#10b981"]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[f"{v:.1%}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#e2e8f0", family="monospace"),
        yaxis=dict(range=[0, 1.15], gridcolor="#334155", tickformat=".0%"),
        xaxis=dict(gridcolor="#334155"),
        margin=dict(t=20, b=10, l=10, r=10),
        height=220,
        showlegend=False,
    )
    return fig


def predict_fn(sepal_length, sepal_width, petal_length, petal_width):
    payload = {
        "sepal_length": sepal_length,
        "sepal_width":  sepal_width,
        "petal_length": petal_length,
        "petal_width":  petal_width,
    }
    try:
        resp = requests.post(f"{FASTAPI_URL}/predict", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to API. Is FastAPI running?", None, ""
    except Exception as e:
        return f"❌ Error: {e}", None, ""

    label      = data["predicted_label"]
    confidence = data["confidence"]
    emoji      = FLOWER_EMOJI.get(label, "🌿")
    probs      = data["probabilities"]

    result_md = f"""
## {emoji} **{label.capitalize()}**
**Confidence:** `{confidence:.1%}`
| Class | Probability |
|-------|------------|
""" + "\n".join(f"| {FLOWER_EMOJI.get(k,'🌿')} {k} | `{v:.4f}` |" for k, v in probs.items())

    chart = make_prob_chart(probs)
    return result_md, chart, f"Predicted class index: {data['predicted_class']}"


def get_model_info():
    try:
        resp = requests.get(f"{FASTAPI_URL}/model/info", timeout=5)
        resp.raise_for_status()
        meta = resp.json()

        fi = meta.get("feature_importances", {})
        fi_rows = "\n".join(f"| {k} | `{v}` |" for k, v in fi.items())

        return f"""
### 📊 Model Info
| Property | Value |
|----------|-------|
| Accuracy | `{meta.get('accuracy', '?')}` |
| Max Depth | `{meta.get('max_depth', '?')}` |
| Leaves | `{meta.get('n_leaves', '?')}` |
| Train samples | `{meta.get('n_train', '?')}` |
| Test samples | `{meta.get('n_test', '?')}` |

### Feature Importances
| Feature | Importance |
|---------|-----------|
{fi_rows}
"""
    except Exception as e:
        return f"⚠️ Could not fetch model info: {e}"


def get_tree_text():
    try:
        clf, meta = load_model()
        return export_text(clf, feature_names=meta["feature_names"])
    except FileNotFoundError:
        return "Model not trained yet. Run: python model/train.py"


# ── Gradio UI ──────────────────────────────────────────────────────────────────

CSS = """
body, .gradio-container { background: #0f172a !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif; }
.gr-panel, .gr-box { background: #1e293b !important; border-color: #334155 !important; }
h1 { color: #a5b4fc !important; }
label { color: #94a3b8 !important; }
.gr-button-primary { background: #6366f1 !important; border: none !important; }
.gr-button-primary:hover { background: #4f46e5 !important; }
"""

with gr.Blocks(title="🌸 Iris Classifier", css=CSS, theme=gr.themes.Base()) as demo:

    gr.Markdown("# 🌸 Iris Decision Tree Classifier\nAdjust the sliders and click **Predict** to classify a flower.")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🔢 Input Features")
            sepal_length = gr.Slider(4.0, 8.0, value=5.1, step=0.1, label="Sepal Length (cm)")
            sepal_width  = gr.Slider(2.0, 4.5, value=3.5, step=0.1, label="Sepal Width (cm)")
            petal_length = gr.Slider(1.0, 7.0, value=1.4, step=0.1, label="Petal Length (cm)")
            petal_width  = gr.Slider(0.1, 2.5, value=0.2, step=0.1, label="Petal Width (cm)")
            predict_btn  = gr.Button("🔍 Predict", variant="primary")

            gr.Examples(
                examples=[
                    [5.1, 3.5, 1.4, 0.2],   # setosa
                    [6.0, 2.9, 4.5, 1.5],   # versicolor
                    [6.7, 3.1, 5.6, 2.4],   # virginica
                ],
                inputs=[sepal_length, sepal_width, petal_length, petal_width],
                label="Quick examples",
            )

        with gr.Column(scale=1):
            gr.Markdown("### 🎯 Prediction")
            result_md   = gr.Markdown("*Click Predict to see results*")
            prob_chart  = gr.Plot(label="Class Probabilities")
            debug_text  = gr.Textbox(label="Debug", visible=False)

    with gr.Accordion("📋 Model Info", open=False):
        info_md  = gr.Markdown()
        info_btn = gr.Button("Load Model Info")
        info_btn.click(fn=get_model_info, outputs=info_md)

    with gr.Accordion("🌲 Tree Structure", open=False):
        tree_out = gr.Textbox(lines=20, label="Decision Tree Rules")
        tree_btn = gr.Button("Show Tree")
        tree_btn.click(fn=get_tree_text, outputs=tree_out)

    predict_btn.click(
        fn=predict_fn,
        inputs=[sepal_length, sepal_width, petal_length, petal_width],
        outputs=[result_md, prob_chart, debug_text],
    )


if __name__ == "__main__":
    demo.launch(server_port=7860, show_error=True)
