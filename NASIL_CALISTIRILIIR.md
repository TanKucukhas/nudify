# 🚀 Sistem Nasıl Çalıştırılır?

## Hızlı Başlangıç (3 Adım)

### ADIM 1: ComfyUI'yi Başlat

```bash
# ComfyUI Desktop'ı aç
open -a ComfyUI

# VEYA tarayıcıda kontrol et
open http://localhost:8188
```

**Kontrol:**
- ComfyUI arayüzü açılmalı
- Sağ üstte "Load Checkpoint" node'u ekle
- Dropdown'da `sdxl_lightning_4step.safetensors` ve `flux1-schnell.safetensors` görünmeli

---

### ADIM 2: Backend Server'ı Başlat

**Yeni terminal aç** ve şunu çalıştır:

```bash
cd ~/workspace/nudify
source venv/bin/activate
python -m backend.server
```

**Göreceğin çıktı:**
```
Starting server on 0.0.0.0:8000
ComfyUI URL: http://localhost:8188
Results directory: results_dev
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Kontrol:**
```bash
# Başka bir terminal'de
curl http://localhost:8000/health
```

Çıktı:
```json
{
  "status": "healthy",
  "comfyui": "connected",
  "comfyui_url": "http://localhost:8188"
}
```

---

### ADIM 3: İlk Deneyi Çalıştır

**Başka bir yeni terminal** aç:

```bash
cd ~/workspace/nudify
source venv/bin/activate

# Önce test et
python scripts/test_api.py

# Sonra deneyi çalıştır
python scripts/run_experiments.py --config configs/exp001_params.json
```

**Göreceğin çıktı:**
```
============================================================
AI Image Generation Lab - Experiment Runner
============================================================

📄 Loading configuration from configs/exp001_params.json
   Experiment ID: exp001
   Number of experiments: 3

✓ Validating configuration...
🔍 Checking API health at http://localhost:8000
   Status: healthy
   ComfyUI: connected

📁 Output directory: results_dev/exp001

🚀 Running 3 experiments...

[1/3] Stage: pose, Seed: 123456
   ✓ Success (15.2s): results_dev/exp001/pose_1234567890_123456.png

[2/3] Stage: pose, Seed: 789012
   ✓ Success (14.8s): results_dev/exp001/pose_1234567891_789012.png

[3/3] Stage: pose, Seed: 345678
   ✓ Success (15.1s): results_dev/exp001/pose_1234567892_345678.png

============================================================
Summary
============================================================
Total experiments: 3
Successful: 3
Failed: 0
Results saved to: results_dev/exp001/results.json
```

---

## 📊 Sonuçları Göster

```bash
# Oluşturulan görselleri listele
ls -lh results_dev/exp001/

# Finder'da aç
open results_dev/exp001/

# Sonuç dosyasını incele
cat results_dev/exp001/results.json
```

---

## 🎨 Yeni Denemeler Oluştur

### Seçenek 1: Mevcut Config'i Düzenle

```bash
# Config'i düzenle
nano configs/exp001_params.json

# VEYA
open -a TextEdit configs/exp001_params.json
```

Değiştirebileceğin parametreler:
- `prompt`: Görsel açıklaması
- `negative_prompt`: İstemediğin şeyler
- `seed`: Rastgele sayı (farklı varyasyonlar için)
- `width`, `height`: Görsel boyutu
- `steps`: Kalite (20-40 arası)
- `cfg_scale`: Prompt'a ne kadar sıkı uyulsun (5-10 arası)
- `model`: "sdxl_lightning" veya "flux_schnell"

### Seçenek 2: Yeni Config Oluştur

```bash
# exp002_params.json oluştur
cp configs/exp001_params.json configs/exp002_params.json

# Düzenle
nano configs/exp002_params.json
```

Değiştir:
```json
{
  "experiment_id": "exp002",  // exp001 → exp002
  "description": "Flux Schnell ile test",
  "experiments": [
    {
      "stage": "pose",
      "prompt": "a beautiful landscape, mountains, sunset, photorealistic",
      "model": "flux_schnell",  // SDXL yerine Flux
      "width": 1024,
      "height": 1024,
      "steps": 25
    }
  ]
}
```

Çalıştır:
```bash
python scripts/run_experiments.py --config configs/exp002_params.json
```

---

## 🔧 Komut Kılavuzu

### API Test
```bash
# Backend sağlık kontrolü
curl http://localhost:8000/health

# API dokümantasyonu
open http://localhost:8000/docs
```

### Config Doğrulama
```bash
# Çalıştırmadan önce test et
python scripts/run_experiments.py \
  --config configs/exp001_params.json \
  --dry-run
```

### Özel Çıktı Klasörü
```bash
python scripts/run_experiments.py \
  --config configs/exp001_params.json \
  --out my_results/test001
```

---

## 🎯 Örnek Kullanım Senaryoları

### 1. Hızlı Test (SDXL Lightning)
```json
{
  "experiment_id": "quick_test",
  "experiments": [{
    "stage": "pose",
    "prompt": "test image, simple composition",
    "model": "sdxl_lightning",
    "width": 512,
    "height": 512,
    "steps": 15
  }]
}
```

### 2. Kaliteli Çıktı (Flux Schnell)
```json
{
  "experiment_id": "high_quality",
  "experiments": [{
    "stage": "pose",
    "prompt": "masterpiece, highly detailed portrait, professional photography",
    "model": "flux_schnell",
    "width": 1024,
    "height": 1024,
    "steps": 30,
    "cfg_scale": 7.5
  }]
}
```

### 3. Çoklu Varyasyon (Farklı Seed'ler)
```json
{
  "experiment_id": "variations",
  "experiments": [
    { "prompt": "sunset landscape", "seed": 100, "model": "sdxl_lightning" },
    { "prompt": "sunset landscape", "seed": 200, "model": "sdxl_lightning" },
    { "prompt": "sunset landscape", "seed": 300, "model": "sdxl_lightning" }
  ]
}
```

---

## ⚠️ Sık Karşılaşılan Sorunlar

### 1. "ComfyUI is not available"
**Çözüm:**
```bash
# ComfyUI'nin çalıştığını kontrol et
curl http://localhost:8188/system_stats

# Çalışmıyorsa başlat
open -a ComfyUI
```

### 2. "Model not found"
**Çözüm:**
```bash
# Modellerin varlığını kontrol et
ls -lh ~/Documents/ComfyUI/models/checkpoints/

# ComfyUI'yi yeniden başlat
```

### 3. "Port 8000 already in use"
**Çözüm:**
```bash
# Başka port kullan
PORT=8001 python -m backend.server

# API çağrılarını da güncelle
python scripts/run_experiments.py \
  --config configs/exp001_params.json \
  --api-url http://localhost:8001
```

### 4. Out of Memory
**Çözüm:**
- Çözünürlüğü düşür: 1024 → 768 → 512
- SDXL Lightning kullan (Flux yerine)
- Diğer uygulamaları kapat

---

## 📋 Günlük İş Akışı

### Sabah Başlangıç
```bash
# 1. ComfyUI'yi başlat
open -a ComfyUI

# 2. Backend'i başlat (terminal 1)
cd ~/workspace/nudify && source venv/bin/activate && python -m backend.server

# 3. Test et (terminal 2)
cd ~/workspace/nudify && source venv/bin/activate && python scripts/test_api.py
```

### Deneme Döngüsü
```bash
# 1. Config oluştur/düzenle
nano configs/my_experiment.json

# 2. Doğrula
python scripts/run_experiments.py --config configs/my_experiment.json --dry-run

# 3. Çalıştır
python scripts/run_experiments.py --config configs/my_experiment.json

# 4. Sonuçları incele
open results_dev/my_experiment/
```

### Akşam Kapatma
```bash
# Backend'i durdur: Ctrl+C (terminal 1'de)
# ComfyUI'yi kapat
```

---

## 🎓 İleri Seviye

### Claude ile Değerlendirme
```bash
# ANTHROPIC_API_KEY ayarla
export ANTHROPIC_API_KEY=your_key_here

# Görselleri değerlendir
python scripts/eval_with_claude.py \
  --images results_dev/exp001 \
  --out results_dev/exp001_eval.json
```

### Makefile Kullanımı
```bash
# Sunucuyu başlat
make server

# Deneme çalıştır
make exp001

# Temizle
make clean
```

---

## 🔗 Yararlı Linkler

- ComfyUI UI: http://localhost:8188
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## ✅ Kontrol Listesi

Çalıştırmadan önce kontrol et:

- [ ] ComfyUI çalışıyor (port 8188)
- [ ] Backend server çalışıyor (port 8000)
- [ ] Modeller yüklü (~/Documents/ComfyUI/models/checkpoints/)
- [ ] venv aktif (`source venv/bin/activate`)
- [ ] Config dosyası geçerli (`--dry-run` ile test et)

Hepsi tamam mı? O zaman başla! 🚀
