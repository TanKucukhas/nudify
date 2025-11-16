# Model Installation Guide

## Quick Reference

Your ComfyUI models directory:
```
~/Documents/ComfyUI/models/checkpoints/
```

## Recommended Models for Mac M4

### 1. SDXL Lightning (Start Here)
**Best for:** Fast iteration, initial pose generation
- **Size:** ~6.5 GB
- **Speed:** ⚡⚡⚡ Very Fast (4 steps)
- **Quality:** ⭐⭐⭐ Good

**Download:**
```bash
cd ~/Documents/ComfyUI/models/checkpoints/
curl -L -o sdxl_lightning_4step.safetensors \
  "https://huggingface.co/ByteDance/SDXL-Lightning/resolve/main/sdxl_lightning_4step_unet.safetensors"
```

### 2. Flux.1 Schnell (Recommended)
**Best for:** Modern quality, strong prompt adherence
- **Size:** ~23 GB
- **Speed:** ⚡⚡ Fast
- **Quality:** ⭐⭐⭐⭐ Excellent

**Download:**
```bash
cd ~/Documents/ComfyUI/models/checkpoints/
curl -L -o flux1-schnell.safetensors \
  "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors"
```

### 3. SDXL Base 1.0 (Optional)
**Best for:** Refinement passes, high quality
- **Size:** ~6.5 GB
- **Speed:** ⚡ Slower
- **Quality:** ⭐⭐⭐⭐ High

**Download:**
```bash
cd ~/Documents/ComfyUI/models/checkpoints/
curl -L -o sd_xl_base_1.0.safetensors \
  "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
```

### 4. Flux.1 Dev (Optional - Highest Quality)
**Best for:** Final detail passes
- **Size:** ~23 GB
- **Speed:** ⚡ Slowest
- **Quality:** ⭐⭐⭐⭐⭐ Best

**Download:**
```bash
cd ~/Documents/ComfyUI/models/checkpoints/
curl -L -o flux1-dev.safetensors \
  "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors"
```

## Installation Methods

### Method 1: Automated Script
```bash
./scripts/download_models.sh
```

### Method 2: Manual Browser Download
1. Visit the HuggingFace links above
2. Download the `.safetensors` files
3. Move to `~/Documents/ComfyUI/models/checkpoints/`

### Method 3: ComfyUI Manager
1. Open ComfyUI Desktop
2. Click "Manager" button
3. Search for models and install

## After Installation

### 1. Verify Installation
```bash
ls -lh ~/Documents/ComfyUI/models/checkpoints/
```

You should see:
- `sdxl_lightning_4step.safetensors`
- `flux1-schnell.safetensors`
- (optional) `sd_xl_base_1.0.safetensors`
- (optional) `flux1-dev.safetensors`

### 2. Restart ComfyUI
If ComfyUI is running, restart it to detect the new models.

### 3. Test in ComfyUI
1. Open ComfyUI at http://localhost:8188
2. Add a "Load Checkpoint" node
3. Click the dropdown - your models should appear
4. Generate a test image

### 4. Verify Backend Integration
The backend code has been updated to use these filenames:
- `sdxl_lightning` → `sdxl_lightning_4step.safetensors`
- `flux_schnell` → `flux1-schnell.safetensors`
- `sdxl_base` → `sd_xl_base_1.0.safetensors`
- `flux_dev` → `flux1-dev.safetensors`

## Storage Requirements

Total space needed:
- **Minimal setup:** ~6.5 GB (SDXL Lightning only)
- **Recommended setup:** ~30 GB (SDXL Lightning + Flux Schnell)
- **Full setup:** ~60 GB (All models)

## Model Usage in Experiments

Update your experiment configs to use these models:

```json
{
  "model": "sdxl_lightning",  // Fast iteration
  "model": "flux_schnell",    // Quality + speed
  "model": "sdxl_base",       // High quality refinement
  "model": "flux_dev"         // Best quality
}
```

## Troubleshooting

### Model doesn't appear in ComfyUI
1. Check the file is in the correct directory
2. Ensure the file extension is `.safetensors`
3. Restart ComfyUI
4. Check ComfyUI logs for errors

### "Model not found" error from backend
1. Verify the model filename matches in `backend/comfyui_client.py`
2. Check the model exists in ComfyUI's checkpoints folder
3. Test the model works in ComfyUI UI first

### Out of memory on Mac
1. Use SDXL Lightning (smaller, faster)
2. Reduce image resolution (768x512 instead of 1024x1024)
3. Close other applications
4. Use batch size = 1

## Additional Models (Optional)

### Stable Diffusion 1.5 (For quick tests)
```bash
curl -L -o sd_v1-5.safetensors \
  "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
```

### ControlNet Models (For pose control)
Place in `~/Documents/ComfyUI/models/controlnet/`

### LoRA Models (For style control)
Place in `~/Documents/ComfyUI/models/loras/`

## Resources

- **HuggingFace:** https://huggingface.co/models
- **ComfyUI Docs:** https://docs.comfy.org
- **SDXL Lightning:** https://huggingface.co/ByteDance/SDXL-Lightning
- **Flux Models:** https://huggingface.co/black-forest-labs
