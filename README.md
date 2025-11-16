# AI Image Generation Lab

A structured framework for systematic AI image generation experimentation using ComfyUI, with automated evaluation via Claude.

## Overview

This project provides a clean, config-driven approach to running image generation experiments on Mac M4 (or any system with ComfyUI). It features:

- **Clean API abstraction** over ComfyUI
- **Multi-stage pipeline** support (pose → anatomy → lighting → detail)
- **Reproducible experiments** via JSON configs
- **Automated evaluation** using Claude's vision capabilities
- **Fast local iteration** optimized for Apple Silicon

## Project Structure

```
.
├── backend/              # FastAPI server
│   ├── server.py        # Main API server
│   ├── comfyui_client.py # ComfyUI integration
│   └── models.py        # Pydantic data models
├── configs/             # Experiment configurations
│   ├── schema.json      # JSON schema for validation
│   ├── base_prompt.json # Prompt templates
│   ├── stages/          # Stage-specific configs
│   └── exp*.json        # Experiment definitions
├── experiments/         # Experiment documentation
│   └── exp001/
│       └── notes.md     # Experiment notes
├── scripts/             # Utility scripts
│   ├── run_experiments.py   # Main experiment runner
│   └── eval_with_claude.py  # Claude evaluation
├── claude/
│   └── prompts/         # Claude prompt templates
├── workflows/
│   └── comfy/           # ComfyUI workflow JSONs
└── results_dev/         # Generated images and results
```

## Setup

### 1. Prerequisites

- Python 3.13+
- ComfyUI Desktop (for Mac) or ComfyUI server
- (Optional) Anthropic API key for Claude evaluation

### 2. Installation

```bash
# Clone and enter the repository
cd nudify

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env to configure ComfyUI URL if needed
```

### 3. ComfyUI Setup

1. Install ComfyUI Desktop for Mac: https://docs.comfy.org/installation/desktop/macos
2. Download models to ComfyUI's models directory:
   - Start with SDXL Lightning for fast iteration
   - Add Flux Schnell for modern quality
   - Add SDXL Base and Flux Dev for final quality

3. Verify ComfyUI is running at `http://localhost:8188`

## Usage

### Quick Start

```bash
# 1. Start the backend server (in one terminal)
source venv/bin/activate
python -m backend.server

# 2. Run an experiment (in another terminal)
source venv/bin/activate
python scripts/run_experiments.py --config configs/exp001_params.json

# 3. (Optional) Evaluate results with Claude
export ANTHROPIC_API_KEY=your_key_here
python scripts/eval_with_claude.py \
    --images results_dev/exp001 \
    --out results_dev/exp001_eval.json
```

### Running the Backend Server

```bash
# Default: http://localhost:8000
python -m backend.server

# Or use uvicorn directly
uvicorn backend.server:app --reload --port 8000
```

### Creating Experiments

1. Create a config file in `configs/`:

```json
{
  "experiment_id": "exp002",
  "description": "Testing different CFG scales",
  "experiments": [
    {
      "stage": "pose",
      "prompt": "full-body portrait, neutral pose, studio lighting",
      "negative_prompt": "blurry, distorted, bad anatomy",
      "seed": 12345,
      "width": 768,
      "height": 1024,
      "steps": 20,
      "cfg_scale": 7.0,
      "model": "sdxl_lightning",
      "extra": {
        "scheduler": "euler_a"
      }
    }
  ]
}
```

2. Run the experiment:

```bash
python scripts/run_experiments.py --config configs/exp002_params.json
```

### Multi-Stage Pipeline

For multi-stage refinement (pose → anatomy → lighting → detail):

1. Run pose generation first
2. Use the output as `input_image` for the next stage
3. Adjust `denoise` parameter (lower values preserve more from input)

Example anatomy stage config:

```json
{
  "stage": "anatomy",
  "prompt": "correct anatomy, realistic hands",
  "negative_prompt": "deformed, extra fingers",
  "input_image": "results_dev/exp001/pose_001.png",
  "steps": 20,
  "cfg_scale": 6.5,
  "model": "sdxl_base",
  "extra": {
    "denoise": 0.35,
    "scheduler": "euler_a"
  }
}
```

## API Reference

### POST /generate

Generate an image.

**Request:**

```json
{
  "experiment_id": "exp001",
  "stage": "pose",
  "prompt": "full-body portrait...",
  "negative_prompt": "blurry...",
  "seed": 123456,
  "width": 768,
  "height": 1024,
  "steps": 20,
  "cfg_scale": 7.0,
  "model": "sdxl_lightning",
  "extra": {
    "denoise": 0.35,
    "scheduler": "euler_a"
  }
}
```

**Response:**

```json
{
  "ok": true,
  "experiment_id": "exp001",
  "stage": "pose",
  "image_path": "results_dev/exp001/pose_1234567890.png",
  "metadata": {
    "seed": 123456,
    "model": "sdxl_lightning",
    "steps": 20,
    "cfg_scale": 7.0,
    "width": 768,
    "height": 1024
  }
}
```

### GET /health

Check API and ComfyUI status.

**Response:**

```json
{
  "status": "healthy",
  "comfyui": "connected",
  "comfyui_url": "http://localhost:8188"
}
```

## Model Selection Guide

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| **SDXL Lightning** | ⚡⚡⚡ | ⭐⭐⭐ | Fast iteration, pose stage |
| **Flux Schnell** | ⚡⚡ | ⭐⭐⭐⭐ | Modern quality, good prompts |
| **SDXL Base** | ⚡ | ⭐⭐⭐⭐ | High quality refinement |
| **Flux Dev** | ⚡ | ⭐⭐⭐⭐⭐ | Best quality, final passes |

## Parameter Guidelines

### Sampling Steps
- **15-20**: Fast iteration (pose stage)
- **20-25**: Balanced quality/speed
- **25-40**: High quality (detail stage)

### CFG Scale
- **5.0-7.0**: Creative, natural results
- **7.0-9.0**: Strong prompt adherence
- **9.0-12.0**: Very strict (can over-saturate)

### Denoise (img2img only)
- **0.2-0.3**: Subtle refinement (detail stage)
- **0.3-0.4**: Moderate changes (anatomy, lighting)
- **0.5-0.7**: Significant alterations

## Claude Evaluation

The evaluation script uses Claude's vision capabilities to score images on:

- **Pose** (1-10): Composition and body position
- **Anatomy** (1-10): Anatomical correctness
- **Lighting** (1-10): Natural illumination
- **Realism** (1-10): Overall photorealistic quality

```bash
export ANTHROPIC_API_KEY=your_key_here
python scripts/eval_with_claude.py \
    --images results_dev/exp001 \
    --out results_dev/exp001_eval.json
```

Output format:

```json
[
  {
    "file": "pose_001.png",
    "pose": 8,
    "anatomy": 7,
    "lighting": 6,
    "realism": 7,
    "notes": "Good composition, minor hand distortion"
  }
]
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black backend/ scripts/
```

### Validating Configs

```bash
# Dry run to validate without executing
python scripts/run_experiments.py \
    --config configs/exp001_params.json \
    --dry-run
```

## Troubleshooting

### ComfyUI Connection Issues

1. Verify ComfyUI is running: `curl http://localhost:8188/system_stats`
2. Check COMFYUI_URL in `.env`
3. View backend health: `curl http://localhost:8000/health`

### Memory Issues on Mac

- Reduce batch size to 1
- Use lower resolutions (768x512 instead of 1024x1024)
- Use Lightning/Schnell models for faster inference
- Close other applications

### Model Not Found

- Verify model files are in ComfyUI's models directory
- Check model names in `backend/comfyui_client.py` line 85
- Update model_map to match your actual checkpoint filenames

## Next Steps

1. **Create ComfyUI workflows** in the UI and save to `workflows/comfy/`
2. **Integrate workflows** with the backend by loading and modifying workflow JSON
3. **Add more models** as needed (SD 1.5 for quick tests)
4. **Implement actual Claude API** in `scripts/eval_with_claude.py`
5. **Deploy to Linux 3090** using Docker once pipelines are proven

## License

MIT

## Contributing

This is a personal lab framework. Feel free to fork and adapt for your needs.
