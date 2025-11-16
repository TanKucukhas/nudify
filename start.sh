#!/bin/bash

echo "🚀 AI Image Generation Lab - Başlatılıyor..."
echo ""

# ComfyUI kontrolü
echo "1️⃣  ComfyUI kontrol ediliyor..."
if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
    echo "   ✅ ComfyUI çalışıyor"
else
    echo "   ⚠️  ComfyUI çalışmıyor!"
    echo "   👉 Şunu çalıştır: open -a ComfyUI"
    echo ""
    read -p "ComfyUI başlattın mı? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ İptal edildi"
        exit 1
    fi
fi

echo ""
echo "2️⃣  Backend server başlatılıyor..."
echo "   http://localhost:8000"
echo ""
echo "   Kapatmak için: Ctrl+C"
echo ""

cd ~/workspace/nudify
source venv/bin/activate
python -m backend.server
