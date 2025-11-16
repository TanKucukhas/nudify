# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI image generation lab designed for fast iteration on Mac M4, with ComfyUI as the backend and a structured experiment framework. The project enables systematic testing of image generation pipelines using various models (SD 1.5, SDXL, FLUX) with automated evaluation.

## Architecture

### Core Components

1. **ComfyUI Backend** (http://localhost:8188)
   - Visual node graph for pipeline design
   - Local HTTP server for image generation
   - Uses Metal (MPS) for Apple Silicon acceleration

2. **FastAPI Wrapper** (recommended)
   - Thin translation layer between clean JSON API and ComfyUI's `/prompt` endpoint
   - Handles image saving to `results_dev/`
   - Implements standardized `/generate` endpoint

3. **Experiment Framework**
   - Config-driven experiment execution
   - Multi-stage pipeline support (pose → anatomy → lighting → detail)
   - Automated metadata tracking

4. **Claude CLI Integration**
   - Config generation
   - Image evaluation and scoring
   - Parameter optimization

### API Contract

The standardized `/generate` endpoint accepts:

```json
{
  "experiment_id": "exp001",
  "stage": "pose",
  "prompt": "full-body portrait, neutral pose, gray background, realistic lighting",
  "negative_prompt": "blurry, distorted, extra limbs, bad anatomy",
  "seed": 123456,
  "width": 768,
  "height": 512,
  "steps": 20,
  "cfg_scale": 6.5,
  "model": "sdxl_lightning",
  "extra": {
    "denoise": 0.35,
    "scheduler": "euler_a"
  }
}
```

Returns:
```json
{
  "ok": true,
  "experiment_id": "exp001",
  "stage": "pose",
  "image_path": "results_dev/exp001/pose_001.png",
  "metadata": { ... }
}
```

## Repository Structure

```
configs/
  schema.json              # JSON schema for experiment configs
  base_prompt.json         # Base prompt templates
  exp001_params.json       # Experiment-specific parameters
  stages/
    pose.json             # Pose generation stage config
    anatomy.json          # Anatomy refinement stage config
    lighting.json         # Lighting adjustment stage config
    detail.json           # Detail enhancement stage config

experiments/
  exp001/
    config.json           # Full experiment configuration
    notes.md              # Experiment notes and findings

scripts/
  run_experiments.py      # Main experiment runner
  eval_with_claude.py     # Claude-powered image evaluation

claude/
  prompts/
    generate_params.md    # Prompt for parameter generation
    evaluate_images.md    # Prompt for image evaluation

workflows/
  comfy/
    pose_pipeline.json    # ComfyUI workflow for pose generation
    full_pipeline.json    # Complete multi-stage pipeline
  n8n/                    # n8n orchestration flows (future)

results_dev/
  exp001/                 # Generated images and metadata per experiment

docker/                   # For Linux+3090 deployment (future)
```

## Image Models

The project uses these models (in order of speed/utility):

1. **SD 1.5** - Fast, lightweight, for sanity checks
   - Repo: `https://huggingface.co/runwayml/stable-diffusion-v1-5`

2. **SDXL Lightning** - Speed-optimized SDXL
   - Repo: `https://huggingface.co/ByteDance/SDXL-Lightning`
   - Primary model for fast iteration at high quality

3. **FLUX.1 [schnell]** - Modern, fast, strong prompt adherence
   - Repo: `https://huggingface.co/black-forest-labs/FLUX.1-schnell`

4. **SDXL Base 1.0** - High quality at 1024×1024
   - Repo: `https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0`

5. **FLUX.1 [dev]** - Highest quality, slower
   - Repo: `https://huggingface.co/black-forest-labs/FLUX.1-dev`

## Development Commands

### Running Experiments

```bash
# Run a single experiment configuration
python scripts/run_experiments.py --config configs/exp001_params.json --out results_dev/exp001

# Evaluate generated images with Claude
python scripts/eval_with_claude.py --images results_dev/exp001 --out results_dev/exp001_eval.json
```

### ComfyUI

```bash
# ComfyUI runs at http://localhost:8188
# Workflows are saved as JSON in workflows/comfy/

# Load a workflow programmatically via API:
# POST http://localhost:8188/prompt
# with ComfyUI workflow JSON payload
```

### Backend Server

```bash
# Start FastAPI wrapper (when implemented)
python backend/server.py

# Test the /generate endpoint
curl -X POST http://localhost:8188/api/generate \
  -H "Content-Type: application/json" \
  -d @configs/exp001_params.json
```

## Key Implementation Details

### Multi-Stage Pipeline

The pipeline processes images through sequential stages:
1. **Pose** - Initial generation with composition and pose
2. **Anatomy** - Refinement pass (img2img, low denoise ~0.35)
3. **Lighting** - Lighting adjustments
4. **Detail** - Final detail enhancement

Each stage can have different prompts, denoise levels, and sampling parameters.

### Experiment Configuration

Experiments are defined in JSON with all parameters explicit:
- Model selection
- Sampling parameters (steps, CFG, scheduler)
- Image dimensions
- Seeds for reproducibility
- Stage-specific overrides

### ComfyUI Integration

Two integration approaches:

1. **Direct API** - Call ComfyUI's `/prompt` with workflow JSON
2. **FastAPI Wrapper** (recommended) - Clean JSON → ComfyUI translation

The wrapper should:
- Accept standardized request format
- Load appropriate workflow from `workflows/comfy/`
- Substitute parameters into workflow nodes
- Call ComfyUI API
- Save outputs with proper naming

### Evaluation Schema

`eval_with_claude.py` outputs structured evaluations:

```json
[
  {
    "file": "pose_001.png",
    "pose": 8,
    "anatomy": 7,
    "lighting": 6,
    "realism": 7,
    "notes": "hands slightly distorted, otherwise solid"
  }
]
```

Scores are 1-10 on: pose, anatomy, lighting, realism.

## Platform-Specific Notes

### Mac M4 (Development)

- ComfyUI uses Metal/MPS acceleration
- Keep batch size = 1, use moderate resolutions (768×512 or 1024×1024)
- SDXL Lightning and Flux schnell are fast enough for iteration
- Models installed in ComfyUI Desktop's model directories

### Linux 3090 (Production - Future)

- Same API contract and structure
- Deploy via Docker
- Higher batch sizes and resolutions possible
- Mirror the Mac setup once pipelines are proven

## Writing Code for This Project

When implementing scripts or backend components:

1. **Respect the API contract** - All backends must implement the same `/generate` interface
2. **Validate configs** - Use `configs/schema.json` for validation
3. **Save metadata** - Always save generation parameters alongside images
4. **Use descriptive experiment IDs** - exp001, exp002, etc.
5. **Handle errors gracefully** - ComfyUI may fail; log and continue with remaining experiments
6. **Enable reproducibility** - Always save seed, model, and all parameters

When generating ComfyUI workflows:
- Base on existing `workflows/comfy/*.json` files
- Keep node structure consistent
- Use clear node IDs for programmatic parameter substitution
- Test in ComfyUI UI before automating

When evaluating images:
- Use Claude's vision capabilities
- Be consistent with scoring criteria
- Save both scores and qualitative notes
- Consider batch evaluation for efficiency
