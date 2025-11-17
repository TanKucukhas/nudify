# Batch Configuration Format

Bu dosya, toplu image generation için JSON config formatını açıklar.

## Kullanım

Batch sayfasında "Paste JSON Config" butonuna tıklayıp JSON array'inizi yapıştırabilirsiniz.

## Format

JSON array içinde her bir obje bir generation request'i temsil eder:

```json
[
  {
    "prompt": "Your prompt here",
    "negative_prompt": "What to avoid (optional)",
    "model": "juggernaut_xl",
    "steps": 25,
    "cfg_scale": 7.0,
    "width": 1024,
    "height": 1024,
    "seed": -1
  }
]
```

## Gerekli Alanlar

- **prompt**: İmage description (zorunlu)

## Opsiyonel Alanlar

- **negative_prompt**: Negatif prompt (default: "blurry, low quality, distorted, bad anatomy")
- **model**: Model alias (default: "juggernaut_xl")
  - Kullanılabilir modeller: `juggernaut_xl`, `sdxl_base`, `flux_fast`
- **steps**: Sampling steps (default: 25)
- **cfg_scale**: CFG Scale (default: 7.0)
- **width**: Görsel genişliği (default: 1024)
- **height**: Görsel yüksekliği (default: 1024)
- **seed**: Random seed (-1 = random, default: -1)
- **stage**: Stage name (default: "batch")

## Önemli Notlar

1. **experiment_id belirtmeyin** - Sistem otomatik olarak `batch_<timestamp>` formatında oluşturur
2. **Sadece prompt zorunlu** - Diğer tüm alanlar opsiyonel
3. **Model belirtilmezse** JuggernautXL kullanılır (default)
4. **Seed -1 ise** her image için random seed kullanılır

## Örnekler

### Minimal (Sadece prompt)

```json
[
  {
    "prompt": "A beautiful landscape"
  },
  {
    "prompt": "A portrait of a person"
  }
]
```

### Full Config

```json
[
  {
    "prompt": "Cyberpunk city, neon lights, rain",
    "negative_prompt": "blurry, low quality",
    "model": "juggernaut_xl",
    "steps": 30,
    "cfg_scale": 7.5,
    "width": 1280,
    "height": 768,
    "seed": 12345
  }
]
```

### Karışık Modeller

```json
[
  {
    "prompt": "Photorealistic portrait",
    "model": "juggernaut_xl",
    "steps": 25
  },
  {
    "prompt": "Fast sketch",
    "model": "flux_fast",
    "steps": 4,
    "cfg_scale": 1.0
  }
]
```

## Örnek Dosya

`configs/example_batch_config.json` dosyasında tam bir örnek bulabilirsiniz.
