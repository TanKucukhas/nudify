#!/bin/bash

# Model download script for ComfyUI
# This script downloads SDXL Lightning and Flux Schnell models

set -e

MODELS_DIR="$HOME/Documents/ComfyUI/models/checkpoints"
TEMP_DIR="/tmp/comfyui_models"

echo "=================================================="
echo "ComfyUI Model Downloader"
echo "=================================================="
echo ""
echo "Target directory: $MODELS_DIR"
echo ""

# Create temp directory
mkdir -p "$TEMP_DIR"

# Function to download with progress
download_model() {
    local url=$1
    local filename=$2
    local description=$3

    echo "Downloading: $description"
    echo "URL: $url"
    echo "File: $filename"
    echo ""

    if [ -f "$MODELS_DIR/$filename" ]; then
        echo "✓ Model already exists, skipping."
        echo ""
        return
    fi

    # Download to temp first
    echo "Downloading to temp directory..."
    curl -L \
        -o "$TEMP_DIR/$filename" \
        --progress-bar \
        "$url"

    # Move to models directory
    mv "$TEMP_DIR/$filename" "$MODELS_DIR/$filename"

    echo "✓ Download complete!"
    echo ""
}

echo "=================================================="
echo "1. SDXL Lightning (4-step, recommended)"
echo "=================================================="
echo "Fast SDXL variant optimized for quick generation"
echo "Size: ~6.5 GB"
echo ""

read -p "Download SDXL Lightning? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    download_model \
        "https://huggingface.co/ByteDance/SDXL-Lightning/resolve/main/sdxl_lightning_4step_unet.safetensors" \
        "sdxl_lightning_4step.safetensors" \
        "SDXL Lightning (4-step)"
fi

echo ""
echo "=================================================="
echo "2. Flux.1 Schnell"
echo "=================================================="
echo "Modern, fast model with excellent prompt adherence"
echo "Size: ~23 GB"
echo ""

read -p "Download Flux.1 Schnell? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    download_model \
        "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors" \
        "flux1-schnell.safetensors" \
        "Flux.1 Schnell"
fi

echo ""
echo "=================================================="
echo "Optional: SDXL Base 1.0"
echo "=================================================="
echo "Original SDXL for highest quality (slower)"
echo "Size: ~6.5 GB"
echo ""

read -p "Download SDXL Base 1.0? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    download_model \
        "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
        "sd_xl_base_1.0.safetensors" \
        "SDXL Base 1.0"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "=================================================="
echo "✓ Installation Complete!"
echo "=================================================="
echo ""
echo "Models installed to: $MODELS_DIR"
echo ""
echo "Next steps:"
echo "1. Restart ComfyUI if it's running"
echo "2. The models should appear in the checkpoint loader"
echo "3. Update backend/comfyui_client.py model_map if needed"
echo ""
ls -lh "$MODELS_DIR"
