#!/bin/bash

echo "🚀 AI Image Generation Lab - Hızlı Başlatma"
echo "============================================"
echo ""

# ComfyUI kontrolü
echo "1️⃣  ComfyUI kontrolü..."
if curl -s http://localhost:8000 | grep -q "ComfyUI"; then
    echo "   ✅ ComfyUI çalışıyor (port 8000)"
else
    echo "   ❌ ComfyUI bulunamadı!"
    echo "   👉 ComfyUI'yi başlat: open -a ComfyUI"
    exit 1
fi

echo ""
echo "2️⃣  Backend başlatılıyor..."
echo "   ComfyUI: http://localhost:8000"
echo "   Backend:  http://localhost:8001"
echo ""
echo "   Kapatmak için: Ctrl+C"
echo ""

cd ~/workspace/nudify
source venv/bin/activate
python -m backend.server
