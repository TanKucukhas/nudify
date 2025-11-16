#!/bin/bash

echo "🚀 ComfyUI Başlatma Yardımcısı"
echo "================================"
echo ""

# ComfyUI'yi başlat
echo "ComfyUI başlatılıyor..."
open -a ComfyUI

echo ""
echo "⏳ ComfyUI yükleniyor... (30 saniye bekleniyor)"
sleep 5

for i in {1..6}; do
    echo -n "."
    sleep 5

    # Her 5 saniyede kontrol et
    if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
        echo ""
        echo ""
        echo "✅ ComfyUI hazır!"
        echo "   URL: http://localhost:8188"
        echo ""

        # Tarayıcıda aç
        open http://localhost:8188

        echo "Backend'i başlatmak için:"
        echo "  ~/workspace/nudify/start.sh"
        exit 0
    fi
done

echo ""
echo ""
echo "⚠️  ComfyUI henüz hazır değil"
echo ""
echo "Yapılacaklar:"
echo "1. ComfyUI penceresini kontrol et"
echo "2. Terminal'de hata mesajı var mı bak"
echo "3. Birkaç dakika daha bekle"
echo ""
echo "Manuel kontrol:"
echo "  curl http://localhost:8188/system_stats"
echo ""
