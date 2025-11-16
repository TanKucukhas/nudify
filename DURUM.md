# Kurulum Durumu

## ✅ Tamamlanan

1. **Proje Yapısı** - Tüm klasörler oluşturuldu
2. **Python Ortamı** - Python 3.13 venv kuruldu, tüm bağımlılıklar yüklendi
3. **Konfigürasyon** - Schema ve config dosyaları hazır
4. **Backend Server** - FastAPI servisi hazır
5. **Script'ler** - run_experiments.py ve eval_with_claude.py hazır
6. **SDXL Lightning** - İndirildi ve hazır (4.8 GB) ✨

## ⚠️ Yapılması Gerekenler

### 1. Flux Schnell İndir (İsteğe Bağlı)
Flux Schnell HuggingFace kimlik doğrulama gerektiriyor:

```bash
# HuggingFace'e giriş yap
huggingface-cli login

# Modeli indir
cd ~/Documents/ComfyUI/models/checkpoints/
huggingface-cli download black-forest-labs/FLUX.1-schnell \
  flux1-schnell.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False
```

VEYA tarayıcıdan manuel indir:
https://huggingface.co/black-forest-labs/FLUX.1-schnell

### 2. ComfyUI'yi Başlat
```bash
# ComfyUI Desktop'ı aç veya
# http://localhost:8188 adresinde çalıştığını doğrula
```

### 3. Backend Server'ı Başlat
```bash
cd /Users/tankucukhas/workspace/nudify
source venv/bin/activate
python -m backend.server
```

### 4. İlk Deneyi Çalıştır
```bash
# Yeni bir terminal'de
cd /Users/tankucukhas/workspace/nudify
source venv/bin/activate
python scripts/run_experiments.py --config configs/exp001_params.json
```

## 📊 Modeller

| Model | Durum | Boyut | Konum |
|-------|-------|-------|-------|
| SDXL Lightning | ✅ İndirildi | 4.8 GB | ~/Documents/ComfyUI/models/checkpoints/ |
| Flux Schnell | ⏳ Bekliyor | 23 GB | Kimlik doğrulama gerekli |

## 🔍 Test Komutları

```bash
# API health check
python scripts/test_api.py

# Config doğrulama
python scripts/run_experiments.py --config configs/exp001_params.json --dry-run

# ComfyUI bağlantısı kontrol
curl http://localhost:8188/system_stats
```

## 💡 İpuçları

1. **SDXL Lightning ile başlayın** - Flux olmadan da çalışır
2. **ComfyUI'de modeli test edin** - Backend'i çalıştırmadan önce
3. **Küçük denemelerle başlayın** - exp001 sadece 3 görsel oluşturuyor

## 📝 Notlar

- Backend kodu SDXL Lightning için güncellendi
- Model dosya isimleri eşleşiyor
- Tüm bağımlılıklar yüklü ve hazır
