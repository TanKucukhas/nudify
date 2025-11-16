# ✅ Kurulum Tamamlandı!

## 🎨 Yüklü Modeller

| Model | Boyut | Durum | Konum |
|-------|-------|-------|-------|
| **SDXL Lightning** | 4.8 GB | ✅ Hazır | ~/Documents/ComfyUI/models/checkpoints/ |
| **Flux Schnell** | 22 GB | ✅ Hazır | ~/Documents/ComfyUI/models/checkpoints/ |

## 🚀 Şimdi Ne Yapmalı?

### 1. ComfyUI'yi Başlat/Yeniden Başlat

```bash
# ComfyUI Desktop'ı aç
open -a ComfyUI

# Veya tarayıcıda
open http://localhost:8188
```

ComfyUI'de "Load Checkpoint" node'unda şunları görmelisin:
- ✅ `sdxl_lightning_4step.safetensors`
- ✅ `flux1-schnell.safetensors`

### 2. Backend Server'ı Başlat

Terminal 1:
```bash
cd ~/workspace/nudify
source venv/bin/activate
python -m backend.server
```

Server şurada çalışacak: http://localhost:8000

### 3. API Test Et

Terminal 2:
```bash
cd ~/workspace/nudify
source venv/bin/activate
python scripts/test_api.py
```

### 4. İlk Deneyi Çalıştır!

```bash
# Config'i doğrula
python scripts/run_experiments.py \
  --config configs/exp001_params.json \
  --dry-run

# Deneyi çalıştır
python scripts/run_experiments.py \
  --config configs/exp001_params.json
```

Bu 3 görsel oluşturacak ve `results_dev/exp001/` klasörüne kaydedecek.

## 📊 Deneme Yapılandırması

`configs/exp001_params.json` şu anda SDXL Lightning kullanıyor.

Flux Schnell denemek için config'i düzenle:
```json
{
  "model": "flux_schnell"  // "sdxl_lightning" yerine
}
```

## 🎯 Hızlı Komutlar

```bash
# API health check
curl http://localhost:8000/health

# ComfyUI health check
curl http://localhost:8188/system_stats

# Server'ı başlat
cd ~/workspace/nudify && source venv/bin/activate && python -m backend.server

# Deneme çalıştır
cd ~/workspace/nudify && source venv/bin/activate && \
  python scripts/run_experiments.py --config configs/exp001_params.json
```

## 📁 Proje Yapısı

```
~/workspace/nudify/
├── backend/              # FastAPI server
├── configs/              # Deneme konfigürasyonları
├── scripts/              # Yardımcı scriptler
├── workflows/            # ComfyUI workflow'ları
└── results_dev/          # Oluşturulan görseller

~/Documents/ComfyUI/models/checkpoints/
├── sdxl_lightning_4step.safetensors    (4.8 GB)
└── flux1-schnell.safetensors           (22 GB)
```

## 🎨 Model Karşılaştırması

### SDXL Lightning
- ⚡ Çok hızlı (4 step)
- 🎯 İyi kalite
- 💡 Hızlı iterasyon için ideal
- 📏 768x1024 önerilen çözünürlük

### Flux Schnell
- ⚡⚡ Hızlı
- 🎯🎯 Mükemmel kalite
- 💡 Prompt'lara çok iyi uyum
- 📏 1024x1024 önerilen çözünürlük

## 🔧 Sorun Giderme

### ComfyUI modeli görmüyor
```bash
# ComfyUI'yi yeniden başlat
# Modellerin doğru yerde olduğunu kontrol et
ls -lh ~/Documents/ComfyUI/models/checkpoints/
```

### Backend bağlanamıyor
```bash
# ComfyUI çalışıyor mu?
curl http://localhost:8188/system_stats

# Backend çalışıyor mu?
curl http://localhost:8000/health
```

### Out of memory hatası
- Küçük çözünürlük kullan (768x512)
- Batch size = 1
- Diğer uygulamaları kapat
- SDXL Lightning kullan (Flux yerine)

## 📚 Dokümantasyon

- `README.md` - Ana dokümantasyon
- `CLAUDE.md` - Claude Code için rehber
- `MODELS.md` - Model kurulum detayları
- `FLUX_KURULUM.md` - Flux indirme rehberi

## 🎓 Sonraki Adımlar

1. ✅ Backend'i başlat
2. ✅ ComfyUI'de modelleri test et
3. ✅ İlk deneyi çalıştır
4. 📝 Sonuçları incele
5. 🎨 Yeni denemeler oluştur
6. 🤖 Claude ile değerlendirme yap (ANTHROPIC_API_KEY gerekli)

## 🎉 Hazırsın!

Tüm sistem kuruldu ve çalışmaya hazır. İyi çalışmalar! 🚀
