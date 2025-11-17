# Model Yönetim Sistemi

## Genel Bakış

Tüm modeller artık merkezi bir yapılandırma dosyasından yönetiliyor. Bu sayede:
- ✅ Model isimlerini tek yerden değiştirme
- ✅ Takma isimler (aliases) kullanarak kısa isimlerle çalışma
- ✅ Önerilen ayarları modelle birlikte saklama
- ✅ Mevcut modelleri otomatik listeleme

## Merkezi Yapılandırma Dosyası

**Dosya:** `configs/models.json`

Bu dosyada tüm kullanılabilir modeller tanımlıdır:

```json
{
  "models": {
    "sdxl_base": {
      "checkpoint_file": "sd_xl_base_1.0.safetensors",
      "type": "sdxl",
      "description": "SDXL Base 1.0 - High quality 1024x1024 generation",
      "enabled": true,
      "recommended_settings": {
        "width": 1024,
        "height": 1024,
        "steps": 30,
        "cfg_scale": 7.0,
        "scheduler": "euler"
      }
    }
  }
}
```

## Kullanım

### 1. Experiment Config'lerinde Model Kullanımı

**Önceki yöntem** (hala çalışır):
```json
{
  "model": "sd_xl_base_1.0.safetensors"
}
```

**Yeni yöntem** (önerilen):
```json
{
  "model": "sdxl_base"
}
```

Sistem otomatik olarak `sdxl_base` → `sd_xl_base_1.0.safetensors` çevirisini yapar.

### 2. Mevcut Modelleri Listeleme

```bash
python scripts/list_models.py
```

Bu komut:
- ComfyUI'de yüklü modelleri gösterir
- Config'de tanımlı modelleri listeler
- Hangi modellerin kullanılabilir olduğunu belirtir

### 3. Yeni Model Ekleme

`configs/models.json` dosyasını düzenle:

```json
{
  "models": {
    "my_custom_model": {
      "checkpoint_file": "my_model_v2.safetensors",
      "type": "sdxl",
      "description": "My custom fine-tuned model",
      "enabled": true,
      "recommended_settings": {
        "width": 768,
        "height": 1024,
        "steps": 40,
        "cfg_scale": 7.5,
        "scheduler": "DPM++ 2M Karras"
      }
    }
  }
}
```

Sonra experiment config'lerinde kullan:

```json
{
  "model": "my_custom_model"
}
```

### 4. Model'i Devre Dışı Bırakma

Bir modeli geçici olarak kullanılamaz yapmak için:

```json
{
  "sdxl_nsfw": {
    "checkpoint_file": "sdxl_nsfw_finetune.safetensors",
    "enabled": false,
    "notes": "Model not downloaded yet"
  }
}
```

`enabled: false` olan modeller kullanılmaya çalışılırsa hata verir.

## Scheduler Aliases

Scheduler isimleri de `models.json`'da tanımlanabilir:

```json
{
  "scheduler_aliases": {
    "dpm_karras": "DPM++ 2M Karras",
    "dpm_sde": "DPM++ SDE Karras",
    "euler_a": "euler_ancestral"
  }
}
```

Kullanım:

```json
{
  "extra": {
    "scheduler": "dpm_karras"  // Otomatik olarak "DPM++ 2M Karras"'a çevrilir
  }
}
```

## Varsayılan Ayarlar

`models.json` içinde global varsayılan ayarlar:

```json
{
  "defaults": {
    "model": "sdxl_base",
    "fallback_model": "sdxl_base",
    "width": 768,
    "height": 1024,
    "steps": 30,
    "cfg_scale": 7.0,
    "scheduler": "euler"
  }
}
```

## Örnek Workflow

### Senaryo: NSFW modeli kullanmak istiyorsun

1. **Model dosyasını ComfyUI'ye yükle:**
   ```bash
   cp ~/Downloads/sdxl_nsfw_v3.safetensors \
     ~/Documents/ComfyUI/models/checkpoints/
   ```

2. **`configs/models.json` dosyasını güncelle:**
   ```json
   {
     "sdxl_nsfw": {
       "checkpoint_file": "sdxl_nsfw_v3.safetensors",
       "type": "sdxl",
       "enabled": true,
       "recommended_settings": {
         "width": 768,
         "height": 1024,
         "steps": 40,
         "cfg_scale": 7.5,
         "scheduler": "DPM++ 2M Karras"
       }
     }
   }
   ```

3. **Experiment config'lerinde kullan:**
   ```bash
   # Tüm "sdxl_base" referanslarını değiştir
   sed -i '' 's/"sdxl_base"/"sdxl_nsfw"/g' configs/exp001_params.json
   ```

4. **Çalıştır:**
   ```bash
   python scripts/run_experiments.py --config configs/exp001_params.json
   ```

## Sorun Giderme

### "Model not found" hatası

```bash
# Mevcut modelleri kontrol et
python scripts/list_models.py

# ComfyUI'de var mı kontrol et
curl http://localhost:8000/object_info/CheckpointLoaderSimple | jq
```

### Model devre dışı hatası

`models.json`'da ilgili modelin `"enabled": true` olduğunu kontrol et.

### Model yüklenmedi hatası

1. Model dosyasının ComfyUI'nin `models/checkpoints/` dizininde olduğunu kontrol et
2. ComfyUI'yi restart et
3. `scripts/list_models.py` ile doğrula

## API Referansı

### ModelManager Sınıfı

```python
from backend.model_manager import ModelManager

manager = ModelManager()

# Model çözümleme
checkpoint = manager.resolve_model("sdxl_base")
# Returns: "sd_xl_base_1.0.safetensors"

# Model validation
is_valid = manager.validate_model("sdxl_base")
# Returns: True/False

# Önerilen ayarları al
settings = manager.get_recommended_settings("sdxl_base")
# Returns: {"width": 1024, "height": 1024, ...}

# Tüm modelleri listele
models = manager.list_available_models()
```

## En İyi Pratikler

1. **Model isimlerinde alias kullan:** Dosya isimleri yerine kısa, anlamlı isimler
2. **Önerilen ayarları tanımla:** Her model için optimal parametreler
3. **Açıklamalar ekle:** Model ne işe yarıyor, ne zaman kullanılmalı
4. **enabled flag kullan:** Olmayan modelleri false olarak işaretle
5. **Scheduler aliases kullan:** "DPM++ 2M Karras" yerine "dpm_karras" gibi

## Sonuç

Bu sistem sayede:
- ✅ Tek bir yerden tüm modelleri yönetebilirsin
- ✅ Experiment config'lerini daha okunabilir yapabilirsin
- ✅ Model değiştirme işini tek satırda yapabilirsin
- ✅ Yeni modeller eklemek çok kolay
