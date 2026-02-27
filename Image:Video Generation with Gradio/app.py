"""
Standalone version — same UI as the Colab notebook.
Run locally with a GPU:  python app.py
"""

import torch
import gradio as gr
import gc
import tempfile
from PIL import Image
from diffusers import (
    StableDiffusionXLPipeline,
    StableDiffusionXLImg2ImgPipeline,
    AnimateDiffPipeline,
    MotionAdapter,
    DDIMScheduler,
)
from diffusers.utils import export_to_video

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE  = torch.float16 if DEVICE == "cuda" else torch.float32

print(f"Device: {DEVICE}")

# ── Lazy pipeline loaders ──────────────────────────────────────────────────────

_pipes: dict = {}

def _load(key, loader_fn):
    if key not in _pipes:
        _pipes[key] = loader_fn()
    return _pipes[key]


def get_txt2img():
    return _load("txt2img", lambda: StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=DTYPE, use_safetensors=True,
        variant="fp16" if DEVICE == "cuda" else None,
    ).to(DEVICE))


def get_img2img():
    return _load("img2img", lambda: StableDiffusionXLImg2ImgPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=DTYPE, use_safetensors=True,
        variant="fp16" if DEVICE == "cuda" else None,
    ).to(DEVICE))


def get_video():
    def _load_video():
        adapter = MotionAdapter.from_pretrained(
            "guoyww/animatediff-motion-adapter-v1-5-2", torch_dtype=DTYPE
        )
        pipe = AnimateDiffPipeline.from_pretrained(
            "SG161222/Realistic_Vision_V5.1_noVAE",
            motion_adapter=adapter, torch_dtype=DTYPE,
        ).to(DEVICE)
        pipe.scheduler = DDIMScheduler.from_config(
            pipe.scheduler.config, beta_schedule="linear",
            clip_sample=False, timestep_spacing="linspace", steps_offset=1,
        )
        if DEVICE == "cuda":
            pipe.enable_vae_slicing()
        return pipe
    return _load("video", _load_video)


def free_memory():
    gc.collect()
    if DEVICE == "cuda":
        torch.cuda.empty_cache()


# ── Generation functions ───────────────────────────────────────────────────────

NEG_DEFAULT = (
    "blurry, low quality, ugly, deformed, watermark, text, "
    "bad anatomy, extra limbs, duplicate"
)


def generate_image(prompt, negative_prompt, width, height, steps, guidance_scale, seed):
    if not prompt.strip():
        return None, "⚠️ Please enter a prompt."
    try:
        gen = torch.Generator(device=DEVICE).manual_seed(int(seed)) if seed >= 0 else None
        result = get_txt2img()(
            prompt=prompt, negative_prompt=negative_prompt or None,
            width=int(width), height=int(height),
            num_inference_steps=int(steps), guidance_scale=float(guidance_scale),
            generator=gen,
        )
        free_memory()
        img = result.images[0]
        return img, f"✅ {img.width}×{img.height} | Steps:{steps} CFG:{guidance_scale} Seed:{seed}"
    except Exception as e:
        return None, f"❌ {e}"


def generate_img2img(init_image, prompt, negative_prompt, strength, steps, guidance_scale, seed):
    if init_image is None:
        return None, "⚠️ Upload an input image."
    if not prompt.strip():
        return None, "⚠️ Please enter a prompt."
    try:
        img = Image.fromarray(init_image).convert("RGB")
        w = max((img.width  // 64) * 64, 512)
        h = max((img.height // 64) * 64, 512)
        img = img.resize((w, h))
        gen = torch.Generator(device=DEVICE).manual_seed(int(seed)) if seed >= 0 else None
        result = get_img2img()(
            prompt=prompt, negative_prompt=negative_prompt or None,
            image=img, strength=float(strength),
            num_inference_steps=int(steps), guidance_scale=float(guidance_scale),
            generator=gen,
        )
        free_memory()
        return result.images[0], f"✅ Strength:{strength} Steps:{steps} CFG:{guidance_scale}"
    except Exception as e:
        return None, f"❌ {e}"


def generate_video(prompt, negative_prompt, num_frames, steps, guidance_scale, fps, seed):
    if not prompt.strip():
        return None, "⚠️ Please enter a prompt."
    try:
        gen = torch.Generator(device=DEVICE).manual_seed(int(seed)) if seed >= 0 else None
        output = get_video()(
            prompt=prompt, negative_prompt=negative_prompt or None,
            num_frames=int(num_frames), num_inference_steps=int(steps),
            guidance_scale=float(guidance_scale), generator=gen,
        )
        free_memory()
        frames = output.frames[0]
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        export_to_video(frames, tmp.name, fps=int(fps))
        return tmp.name, f"✅ {len(frames)} frames @ {fps}fps | Steps:{steps} CFG:{guidance_scale}"
    except Exception as e:
        return None, f"❌ {e}"


# ── Gradio UI ──────────────────────────────────────────────────────────────────

CSS = """
.gradio-container { max-width: 900px !important; margin: auto !important; }
#title { text-align: center; margin-bottom: 8px; }
"""

with gr.Blocks(css=CSS, theme=gr.themes.Soft(), title="🎨 AI Generator") as demo:

    gr.HTML(f'<div id="title"><h1>🎨 AI Image & Video Generator</h1>'
            f'<p>SDXL · AnimateDiff · {DEVICE.upper()}</p></div>')

    with gr.Tab("🖼️ Text → Image"):
        with gr.Row():
            with gr.Column():
                t2i_prompt = gr.Textbox(label="Prompt", lines=3,
                    placeholder="A majestic wolf howling at the moon, digital art, 4K...")
                t2i_neg    = gr.Textbox(label="Negative Prompt", value=NEG_DEFAULT, lines=2)
                with gr.Row():
                    t2i_w = gr.Slider(512, 1024, 1024, step=64, label="Width")
                    t2i_h = gr.Slider(512, 1024, 1024, step=64, label="Height")
                with gr.Row():
                    t2i_steps = gr.Slider(10, 50, 30, step=1, label="Steps")
                    t2i_cfg   = gr.Slider(1, 15, 7.5, step=0.5, label="Guidance Scale")
                t2i_seed = gr.Number(value=42, label="Seed (-1 = random)")
                gr.Button("✨ Generate", variant="primary").click(
                    generate_image,
                    [t2i_prompt, t2i_neg, t2i_w, t2i_h, t2i_steps, t2i_cfg, t2i_seed],
                    [gr.Image(label="Output", type="pil"),
                     gr.Textbox(label="Status", interactive=False)],
                )
            with gr.Column():
                t2i_out    = gr.Image(label="Output", type="pil", height=420)
                t2i_status = gr.Textbox(label="Status", interactive=False)

    with gr.Tab("🔄 Image → Image"):
        with gr.Row():
            with gr.Column():
                i2i_input  = gr.Image(label="Input Image", type="numpy", height=200)
                i2i_prompt = gr.Textbox(label="Prompt", lines=2,
                    placeholder="Transform into watercolor painting...")
                i2i_neg      = gr.Textbox(label="Negative Prompt", value=NEG_DEFAULT, lines=2)
                with gr.Row():
                    i2i_strength = gr.Slider(0.1, 1.0, 0.75, step=0.05, label="Strength")
                    i2i_steps    = gr.Slider(10, 50, 30, step=1, label="Steps")
                with gr.Row():
                    i2i_cfg  = gr.Slider(1, 15, 7.5, step=0.5, label="Guidance Scale")
                    i2i_seed = gr.Number(value=42, label="Seed")
                i2i_btn = gr.Button("🔄 Transform", variant="primary")
            with gr.Column():
                i2i_out    = gr.Image(label="Output", type="pil", height=420)
                i2i_status = gr.Textbox(label="Status", interactive=False)
        i2i_btn.click(generate_img2img,
            [i2i_input, i2i_prompt, i2i_neg, i2i_strength, i2i_steps, i2i_cfg, i2i_seed],
            [i2i_out, i2i_status])

    with gr.Tab("🎬 Text → Video"):
        with gr.Row():
            with gr.Column():
                vid_prompt = gr.Textbox(label="Prompt", lines=3,
                    placeholder="Ocean waves crashing, cinematic, slow motion...")
                vid_neg    = gr.Textbox(label="Negative Prompt", value=NEG_DEFAULT, lines=2)
                with gr.Row():
                    vid_frames = gr.Slider(8, 32, 16, step=4, label="Frames")
                    vid_fps    = gr.Slider(4, 16, 8, step=1, label="FPS")
                with gr.Row():
                    vid_steps = gr.Slider(10, 50, 25, step=1, label="Steps")
                    vid_cfg   = gr.Slider(1, 15, 7.5, step=0.5, label="Guidance Scale")
                vid_seed = gr.Number(value=42, label="Seed")
                vid_btn  = gr.Button("🎬 Generate Video", variant="primary")
            with gr.Column():
                vid_out    = gr.Video(label="Output", height=380)
                vid_status = gr.Textbox(label="Status", interactive=False)
        vid_btn.click(generate_video,
            [vid_prompt, vid_neg, vid_frames, vid_steps, vid_cfg, vid_fps, vid_seed],
            [vid_out, vid_status])


if __name__ == "__main__":
    demo.launch(share=True)
