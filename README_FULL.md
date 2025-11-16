# AI Image Generation Lab 🎨

Sistematik AI görsel üretimi için ComfyUI tabanlı, tam otomatik deneysel çerçeve.

## 📋 Proje Özeti

Mac M4 üzerinde hızlı iterasyon için tasarlanmış, config-driven görsel üretim sistemi. FastAPI backend, ComfyUI entegrasyonu ve Claude tabanlı otomatik değerlendirme içerir.

## ✨ Özellikler

- ✅ **Temiz API Abstraction** - ComfyUI üzerinde RESTful API
- ✅ **Çoklu Model Desteği** - SDXL, Flux ve diğerleri
- ✅ **Config-Driven Experiments** - JSON ile tam kontrol
- ✅ **Otomatik Değerlendirme** - Claude vision ile kalite skorlama
- ✅ **Multi-Stage Pipeline** - pose → anatomy → lighting → detail
- ✅ **Reproducible** - Seed ve parametre takibi
- ✅ **Apple Silicon Optimized** - Metal/MPS hızlandırma

## 🚀 Hızlı Başlangıç

### Gereksinimler

- macOS (Apple Silicon veya Intel)
- Python 3.11+
- ComfyUI Desktop
- 30+ GB disk alanı (modeller için)

### Kurulum

```bash
# Repository'yi klonla
git clone <repo-url>
cd nudify

# Sanal ortam oluştur
python3.13 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment dosyası oluştur
cp .env.example .env
```

### Modelleri İndir

```bash
# HuggingFace'e giriş yap
huggingface-cli login

# Model erişimi iste (tarayıcıda)
# https://huggingface.co/black-forest-labs/FLUX.1-schnell

# Modelleri indir
cd ~/Documents/ComfyUI/models/checkpoints/

# Flux Schnell (TAM MODEL - önerilen)
huggingface-cli download black-forest-labs/FLUX.1-schnell \
  flux1-schnell.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False

# SDXL Base (SDXL Lightning için gerekli)
curl -L -o sd_xl_base_1.0.safetensors \
  "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
```

### Çalıştır

```bash
# 1. ComfyUI'yi başlat
open -a ComfyUI

# 2. Backend'i başlat (yeni terminal)
~/workspace/nudify/quick_start.sh

# 3. Deneme çalıştır (başka terminal)
~/workspace/nudify/run_experiment.sh
```

## 📁 Proje Yapısı

```
nudify/
├── backend/              # FastAPI server
│   ├── server.py        # Ana API servisi
│   ├── comfyui_client.py # ComfyUI entegrasyonu
│   └── models.py        # Pydantic data models
├── configs/             # Deneyim konfigürasyonları
│   ├── schema.json      # JSON schema
│   ├── base_prompt.json # Prompt şablonları
│   ├── stages/          # Stage konfigürasyonları
│   └── exp*.json        # Deneyim tanımları
├── scripts/             # Yardımcı scriptler
│   ├── run_experiments.py   # Ana runner
│   ├── eval_with_claude.py  # Claude değerlendirme
│   └── test_api.py          # API test
├── claude/
│   └── prompts/         # Claude prompt şablonları
├── workflows/
│   └── comfy/           # ComfyUI workflow JSON'ları
└── results_dev/         # Oluşturulan görseller
```

## 🎮 Kullanım

### Basit Deneme

```bash
# Varsayılan config ile çalıştır
~/workspace/nudify/run_experiment.sh

# Özel config ile
~/workspace/nudify/run_experiment.sh configs/my_experiment.json
```

### Config Oluşturma

```json
{
  "experiment_id": "exp002",
  "description": "Flux Schnell landscape test",
  "experiments": [
    {
      "stage": "pose",
      "prompt": "beautiful mountain landscape, sunset, photorealistic",
      "negative_prompt": "blurry, distorted, low quality",
      "seed": 12345,
      "width": 1024,
      "height": 1024,
      "steps": 25,
      "cfg_scale": 7.0,
      "model": "flux_schnell",
      "extra": {
        "scheduler": "euler"
      }
    }
  ]
}
```

### Manuel API Kullanımı

```bash
# Health check
curl http://localhost:8001/health

# Görsel oluştur
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d @configs/exp001_params.json
```

## 🎨 Desteklenen Modeller

| Model | Boyut | Hız | Kalite | Kullanım |
|-------|-------|-----|--------|----------|
| **Flux Schnell** | 22 GB | ⚡⚡ | ⭐⭐⭐⭐ | Önerilen - tam model |
| **SDXL Base** | 6.5 GB | ⚡ | ⭐⭐⭐⭐ | Kaliteli çıktı |
| **SDXL Lightning** | 4.8 GB | ⚡⚡⚡ | ⭐⭐⭐ | Hızlı iterasyon (Base gerekli) |

## 🔧 Konfigürasyon

### Environment Variables (.env)

```bash
# ComfyUI Configuration
COMFYUI_URL=http://localhost:8000

# Server Configuration
HOST=0.0.0.0
PORT=8001

# Results Directory
RESULTS_DIR=results_dev

# Claude API (opsiyonel - değerlendirme için)
ANTHROPIC_API_KEY=your_key_here
```

### Geçerli Scheduler İsimleri

```
euler                - Hızlı, kararlı (önerilen)
euler_ancestral      - Yaratıcı
heun                 - Yüksek kalite
dpm_2                - DPM solver
ddim                 - DDIM sampler
```

## 🤖 Claude Değerlendirme

```bash
# API key ayarla
export ANTHROPIC_API_KEY=your_key

# Görselleri değerlendir
python scripts/eval_with_claude.py \
  --images results_dev/exp001 \
  --out results_dev/exp001_eval.json
```

Çıktı:
```json
[
  {
    "file": "pose_001.png",
    "pose": 8,
    "anatomy": 7,
    "lighting": 6,
    "realism": 7,
    "notes": "Good composition, minor issues..."
  }
]
```

## 📊 API Endpoints

### `GET /health`
Sistem sağlık kontrolü

### `POST /generate`
Görsel oluştur

**Request:**
```json
{
  "experiment_id": "exp001",
  "stage": "pose",
  "prompt": "...",
  "model": "flux_schnell",
  "width": 1024,
  "height": 1024,
  "steps": 25,
  "cfg_scale": 7.0
}
```

**Response:**
```json
{
  "ok": true,
  "experiment_id": "exp001",
  "stage": "pose",
  "image_path": "results_dev/exp001/pose_123.png",
  "metadata": {...}
}
```

## 🛠️ Yardımcı Scriptler

```bash
# Sistem durumu kontrolü
~/workspace/nudify/check_status.sh

# Backend başlat
~/workspace/nudify/quick_start.sh

# ComfyUI başlat ve bekle
~/workspace/nudify/comfyui_baslat.sh

# Tüm servisleri yeniden başlat
~/workspace/nudify/restart_all.sh
```

## ⚙️ Port Yapılandırması

```
ComfyUI:  http://localhost:8000
Backend:  http://localhost:8001
API Docs: http://localhost:8001/docs
```

## 🔍 Sorun Giderme

### ComfyUI Bağlanmıyor

```bash
# Port kontrolü
lsof -i :8000

# Manuel başlat
open -a ComfyUI

# Sistem kontrolü
~/workspace/nudify/check_status.sh
```

### Model Bulunamıyor

```bash
# Modelleri kontrol et
ls -lh ~/Documents/ComfyUI/models/checkpoints/

# ComfyUI'yi yeniden başlat
pkill -f ComfyUI
open -a ComfyUI
```

### Out of Memory

- Çözünürlüğü düşür (1024 → 768 → 512)
- Flux yerine SDXL kullan
- Diğer uygulamaları kapat
- Batch size = 1 kullan

### Sampler Hatası

```
Error: sampler_name 'euler_a' not in list
```

Düzelt: `euler_a` → `euler_ancestral` veya `euler`

## 📚 Dokümantasyon

- `CLAUDE.md` - Claude Code için rehber
- `MODELS.md` - Model kurulum detayları
- `FLUX_KURULUM.md` - Flux indirme rehberi
- `NASIL_CALISTIRILIIR.md` - Detaylı kullanım
- `HATA_COZUMU.md` - Yaygın sorunlar
- `SAMPLER_ISIMLERI.md` - Scheduler referansı

## 🎯 İleri Seviye

### Multi-Stage Pipeline

```json
{
  "experiment_id": "multistage",
  "experiments": [
    {
      "stage": "pose",
      "prompt": "portrait...",
      "model": "flux_schnell"
    },
    {
      "stage": "anatomy",
      "prompt": "correct anatomy...",
      "input_image": "results_dev/multistage/pose_001.png",
      "model": "sdxl_base",
      "extra": {"denoise": 0.35}
    }
  ]
}
```

### Toplu Değerlendirme

```bash
# Tüm denemeleri değerlendir
for exp in results_dev/exp*; do
  python scripts/eval_with_claude.py \
    --images "$exp" \
    --out "${exp}_eval.json"
done
```

## 🤝 Katkıda Bulunma

Bu kişisel bir lab projesidir, ancak fork'layıp kendi ihtiyaçlarınıza göre özelleştirebilirsiniz.

## 📝 Lisans

MIT

## 🙏 Teşekkürler

- ComfyUI ekibine
- Stability AI ve Black Forest Labs'e modeller için
- Anthropic'e Claude için

## 📧 Destek

Sorunlar için:
- HATA_COZUMU.md dosyasına bakın
- GitHub Issues kullanın
- CLAUDE.md'yi inceleyin

---

**Oluşturulma:** 2024-11-16
**Son Güncelleme:** 2024-11-16
**Versiyon:** 1.0.0
