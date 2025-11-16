#!/bin/bash

echo "🔍 Sistem Durum Kontrolü"
echo "================================"
echo ""

# ComfyUI kontrolü
echo "1️⃣  ComfyUI (port 8188)"
if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
    echo "   ✅ Çalışıyor"
else
    echo "   ❌ Çalışmıyor!"
    echo "   👉 Başlatmak için: open -a ComfyUI"
fi

echo ""

# Backend kontrolü
echo "2️⃣  Backend (port 8000)"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    STATUS=$(curl -s http://localhost:8000/health | grep -o '"comfyui":"[^"]*' | cut -d'"' -f4)
    if [ "$STATUS" = "connected" ]; then
        echo "   ✅ Çalışıyor (ComfyUI'ye bağlı)"
    else
        echo "   ⚠️  Çalışıyor ama ComfyUI'ye bağlanamıyor"
    fi
else
    echo "   ❌ Çalışmıyor!"
    echo "   👉 Başlatmak için: ~/workspace/nudify/start.sh"
fi

echo ""

# Model kontrolü
echo "3️⃣  Modeller"
MODELS_DIR=~/Documents/ComfyUI/models/checkpoints

if [ -f "$MODELS_DIR/sdxl_lightning_4step.safetensors" ]; then
    SIZE=$(du -h "$MODELS_DIR/sdxl_lightning_4step.safetensors" | cut -f1)
    echo "   ✅ SDXL Lightning ($SIZE)"
else
    echo "   ❌ SDXL Lightning bulunamadı"
fi

if [ -f "$MODELS_DIR/flux1-schnell.safetensors" ]; then
    SIZE=$(du -h "$MODELS_DIR/flux1-schnell.safetensors" | cut -f1)
    echo "   ✅ Flux Schnell ($SIZE)"
else
    echo "   ❌ Flux Schnell bulunamadı"
fi

echo ""
echo "================================"

# Özet
COMFY_OK=$(curl -s http://localhost:8188/system_stats > /dev/null 2>&1 && echo "yes" || echo "no")
BACKEND_OK=$(curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "yes" || echo "no")

if [ "$COMFY_OK" = "yes" ] && [ "$BACKEND_OK" = "yes" ]; then
    echo "✅ Sistem hazır! Deneme çalıştırabilirsin."
    echo ""
    echo "Çalıştırmak için:"
    echo "  ~/workspace/nudify/run_experiment.sh"
else
    echo "⚠️  Bazı servisler çalışmıyor!"
    echo ""
    if [ "$COMFY_OK" = "no" ]; then
        echo "❌ ComfyUI'yi başlat: open -a ComfyUI"
    fi
    if [ "$BACKEND_OK" = "no" ]; then
        echo "❌ Backend'i başlat: ~/workspace/nudify/start.sh"
    fi
fi
echo ""
