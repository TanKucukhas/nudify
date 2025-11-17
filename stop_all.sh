#!/bin/bash

echo "🛑 Tüm Servisleri Durdur"
echo "======================="
echo ""

echo "Durduruluyor..."
pkill -f ComfyUI 2>/dev/null
pkill -f "backend.server" 2>/dev/null
pkill -f "next dev" 2>/dev/null

sleep 2

echo ""
echo "✅ Tüm servisler durduruldu"
echo ""
echo "Kontrol:"
echo "  lsof -i :8000  # ComfyUI"
echo "  lsof -i :8001  # Backend"
echo "  lsof -i :4000  # Admin"
