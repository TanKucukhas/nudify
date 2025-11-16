#!/bin/bash

cd ~/workspace/nudify
source venv/bin/activate

CONFIG=${1:-configs/exp001_params.json}
API_URL="http://localhost:8001"

echo "🎨 AI Image Generation Lab"
echo "================================"
echo ""
echo "Config: $CONFIG"
echo "API:    $API_URL"
echo ""

# Test API
echo "🔍 API test ediliyor..."
curl -s "$API_URL/health" > /dev/null || {
    echo "❌ Backend çalışmıyor!"
    echo "   Başlatmak için: ~/workspace/nudify/quick_start.sh"
    exit 1
}

echo ""
echo "🚀 Deneme başlatılıyor..."
echo ""

python scripts/run_experiments.py --config "$CONFIG" --api-url "$API_URL"

# Sonuçları göster
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tamamlandı!"
    echo ""
    echo "📁 Sonuçlar:"

    # Experiment ID'yi config'den al
    EXP_ID=$(grep -o '"experiment_id": "[^"]*' "$CONFIG" | cut -d'"' -f4)

    if [ -d "results_dev/$EXP_ID" ]; then
        ls -lh "results_dev/$EXP_ID/"
        echo ""
        read -p "Sonuçları Finder'da açmak ister misin? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "results_dev/$EXP_ID/"
        fi
    fi
fi
