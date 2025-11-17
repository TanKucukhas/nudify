#!/bin/bash

echo "🔄 Tüm Servisleri Yeniden Başlat"
echo "================================"
echo ""

# Her şeyi kapat
echo "1️⃣  Servisleri kapatıyor..."
pkill -f ComfyUI 2>/dev/null
pkill -f "backend.server" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 2
echo "   ✅ Kapatıldı"
echo ""

# ComfyUI'yi komut satırından başlat (Desktop app yerine)
echo "2️⃣  ComfyUI başlatılıyor (headless mode)..."
COMFY_VENV="/Users/tankucukhas/Documents/ComfyUI/.venv"
COMFY_DIR="/Applications/ComfyUI.app/Contents/Resources/ComfyUI"

if [ -d "$COMFY_VENV" ] && [ -d "$COMFY_DIR" ]; then
    cd "$COMFY_DIR"
    $COMFY_VENV/bin/python main.py \
        --listen 127.0.0.1 \
        --port 8000 \
        --base-directory /Users/tankucukhas/Documents/ComfyUI \
        > /tmp/comfyui.log 2>&1 &

    echo "   ⏳ 15 saniye bekleniyor..."

    # Hazır olmasını bekle
    for i in {1..15}; do
        sleep 1
        if curl -s http://localhost:8000/system_stats > /dev/null 2>&1; then
            echo ""
            echo "   ✅ ComfyUI hazır (port 8000)"
            break
        fi
        echo -n "."
    done
else
    echo "   ❌ ComfyUI dizini bulunamadı!"
    echo "   Lütfen Desktop uygulamasını kullanın veya yolu güncelleyin"
    exit 1
fi

echo ""
echo ""

# Port kontrolü
if curl -s http://localhost:8000/system_stats > /dev/null 2>&1; then
    echo "3️⃣  Backend başlatılıyor..."
    cd ~/workspace/nudify
    source venv/bin/activate
    python -m backend.server > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!

    sleep 3

    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "   ✅ Backend hazır (port 8001)"
    else
        echo "   ❌ Backend başlamadı!"
        tail -20 /tmp/backend.log
        exit 1
    fi

    echo ""
    echo "4️⃣  Admin panel başlatılıyor..."
    cd ~/workspace/nudify/admin
    PORT=4000 npm run dev > /tmp/admin.log 2>&1 &
    ADMIN_PID=$!

    sleep 3

    if curl -s http://localhost:4000 > /dev/null 2>&1; then
        echo "   ✅ Admin panel hazır (port 4000)"
    else
        echo "   ⚠️  Admin panel başlıyor... (birkaç saniye sürebilir)"
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ TÜM SERVİSLER ÇALIŞIYOR"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📍 ComfyUI:     http://localhost:8000"
    echo "📍 Backend API: http://localhost:8001"
    echo "📍 Admin Panel: http://localhost:4000"
    echo ""
    echo "📋 Log dosyaları:"
    echo "   - ComfyUI:  /tmp/comfyui.log"
    echo "   - Backend:  /tmp/backend.log"
    echo "   - Admin:    /tmp/admin.log"
    echo ""
    echo "🛑 Durdurmak için:"
    echo "   ./stop_all.sh"
    echo ""
else
    echo "❌ ComfyUI port 8000'de başlamadı!"
    echo ""
    echo "Log dosyasını kontrol edin:"
    echo "  tail -50 /tmp/comfyui.log"
    echo ""
    echo "Manuel başlatma:"
    echo "  cd $COMFY_DIR"
    echo "  $COMFY_VENV/bin/python main.py --listen 127.0.0.1 --port 8000"
fi
