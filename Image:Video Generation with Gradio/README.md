# 🎨 Image & Video Generator — Colab + Gradio

Generate images and videos with AI using Stable Diffusion XL and AnimateDiff,
with a Gradio UI. Designed to run on **Google Colab (T4 GPU)**.

## Quick Start — Google Colab

1. Open `image_video_generator.ipynb` in Google Colab
2. **Runtime → Change runtime type → T4 GPU**
3. Run all cells top to bottom
4. Click the **public Gradio link** that appears after Cell 5

## Features

| Tab | Model | What it does |
|-----|-------|-------------|
| 🖼️ Text → Image | SDXL 1.0 | Generate images from a text prompt |
| 🔄 Image → Image | SDXL 1.0 | Transform an uploaded image with a prompt |
| 🎬 Text → Video | AnimateDiff v1.5.2 | Generate short animated MP4 clips |

## Local Run (requires GPU)

```bash
pip install -r requirements.txt
python app.py
```

## Notebook Structure

| Cell | Description |
|------|-------------|
| 1 | Install pip packages |
| 2 | Imports + GPU check |
| 3 | Lazy pipeline loaders (models downloaded on first use) |
| 4 | `generate_image`, `generate_img2img`, `generate_video` functions |
| 5 | Gradio UI with 3 tabs + `demo.launch(share=True)` |

## Tips

- **VRAM issues on video?** Lower Frames from 16 → 8
- **Slow generation?** Reduce Steps (20 is fine for most prompts)
- **Better quality:** Add `4K, highly detailed, cinematic, professional photography` to prompts
- **Guidance Scale:** 7–8 for balanced; higher = follows prompt more strictly
- Models are downloaded automatically from Hugging Face Hub on first run (~6–15 GB total)
