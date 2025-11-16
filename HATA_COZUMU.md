# ⚠️ Hata Çözümü: 404 Not Found

## Sorun

Backend şu hatayı veriyor:
```
INFO: 127.0.0.1:60219 - "HEAD /queue HTTP/1.1" 404 Not Found
```

## Neden?

**ComfyUI çalışmıyor!**

Backend, ComfyUI'ye bağlanmaya çalışıyor ama ComfyUI port 8188'de çalışmıyor.

## ✅ Çözüm

### ADIM 1: ComfyUI'yi Başlat

```bash
# ComfyUI Desktop'ı aç
open -a ComfyUI
```

**VEYA** tarayıcıda kontrol et:
```bash
open http://localhost:8188
```

### ADIM 2: ComfyUI'nin Çalıştığını Doğrula

```bash
# Bu komut JSON döndürmeli
curl http://localhost:8188/system_stats
```

Çıktı şuna benzer olmalı:
```json
{
  "system": {
    "os": "Darwin",
    ...
  }
}
```

### ADIM 3: Backend'i Yeniden Başlat

Backend'in çalıştığı terminalde:
1. `Ctrl+C` ile durdur
2. Tekrar başlat:
```bash
python -m backend.server
```

Şimdi şunu görmelisin:
```
🔍 Checking API health at http://localhost:8000
   Status: healthy
   ComfyUI: connected  ✅
```

## 🔍 Hızlı Kontrol

### ComfyUI Çalışıyor mu?
```bash
curl http://localhost:8188/system_stats
```

✅ **Çalışıyor** → JSON döner
❌ **Çalışmıyor** → Hata veya boş

### Backend Çalışıyor mu?
```bash
curl http://localhost:8000/health
```

Çıktı:
```json
{
  "status": "healthy",
  "comfyui": "connected"  ← Bu "connected" olmalı!
}
```

## 🚀 Doğru Başlangıç Sırası

**1. İlk:** ComfyUI
```bash
open -a ComfyUI
```

**2. Sonra:** Backend
```bash
cd ~/workspace/nudify
source venv/bin/activate
python -m backend.server
```

**3. En son:** Deneme
```bash
cd ~/workspace/nudify
source venv/bin/activate
python scripts/run_experiments.py --config configs/exp001_params.json
```

## ⚡ Hızlı Script

```bash
# Tek komutla kontrol et
~/workspace/nudify/check_status.sh
```

Bu script:
- ✅ ComfyUI çalışıyor mu?
- ✅ Backend çalışıyor mu?
- ✅ Modeller yüklü mü?

kontrol eder.

## 🔧 Diğer Olası Sorunlar

### Port Çakışması

Eğer ComfyUI farklı bir portta çalışıyorsa:

```bash
# .env dosyasını düzenle
nano .env

# Değiştir:
COMFYUI_URL=http://localhost:XXXX  # 8188 yerine doğru port
```

### ComfyUI Dondu

```bash
# ComfyUI'yi tamamen kapat
pkill -f ComfyUI

# Yeniden başlat
open -a ComfyUI
```

## 📝 Kontrol Listesi

Çalıştırmadan önce:

- [ ] ComfyUI açık ve çalışıyor
- [ ] http://localhost:8188 tarayıcıda açılıyor
- [ ] `curl http://localhost:8188/system_stats` JSON döndürüyor
- [ ] Backend başlatıldı
- [ ] `curl http://localhost:8000/health` "connected" diyor
- [ ] venv aktif

Hepsi ✅ ise denemeyi çalıştır!
