#!/bin/bash

echo "🔄 Tüm Servisleri Yeniden Başlat"
echo "================================"
echo ""

# Her şeyi kapat
echo "1️⃣  Servisleri kapatıyor..."
pkill -f ComfyUI 2>/dev/null
pkill -f "backend.server" 2>/dev/null
sleep 2
echo "   ✅ Kapatıldı"
echo ""

# ComfyUI'yi başlat
echo "2️⃣  ComfyUI başlatılıyor..."
open -a ComfyUI
echo "   ⏳ 30 saniye bekleniyor..."

# Hazır olmasını bekle
for i in {1..30}; do
    sleep 1
    if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
        echo ""
        echo "   ✅ ComfyUI hazır (port 8188)"
        break
    fi
    echo -n "."
done

echo ""
echo ""

# Port kontrolü
if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
    echo "3️⃣  Backend başlatılıyor..."
    echo "   http://localhost:8000"
    echo ""
    echo "   Kapatmak için: Ctrl+C"
    echo ""
    cd ~/workspace/nudify
    source venv/bin/activate
    python -m backend.server
else
    echo "❌ ComfyUI port 8188'de başlamadı!"
    echo ""
    echo "Manuel kontrol:"
    echo "  lsof -i :8188"
    echo "  lsof -i :8000"
fi
