# ComfyUI Geçerli Sampler İsimleri

Config dosyalarında `scheduler` parametresi için kullanılabilecek değerler:

## ✅ Geçerli İsimler:

```
euler                    - En hızlı, kararlı
euler_ancestral          - Daha yaratıcı (eski: euler_a)
heun                     - Daha yüksek kalite, yavaş
dpm_2                    - DPM solver
dpm_2_ancestral          - DPM yaratıcı mod
lms                      - LMS solver
dpm_fast                 - Hızlı DPM
ddim                     - DDIM sampler
```

## 📝 Config Örnekleri:

### Hızlı (Önerilen):
```json
{
  "extra": {
    "scheduler": "euler"
  }
}
```

### Yaratıcı:
```json
{
  "extra": {
    "scheduler": "euler_ancestral"
  }
}
```

### Kaliteli:
```json
{
  "extra": {
    "scheduler": "heun"
  }
}
```

## ❌ Eski/Geçersiz İsimler:

- `euler_a` → `euler_ancestral` kullan
- `dpm` → `dpm_2` kullan

## 🔍 Tüm Listeyiİ Görmek İçin:

```bash
curl -s http://localhost:8000/object_info/KSampler | \
  python3 -c "import sys, json; print('\n'.join(json.load(sys.stdin)['KSampler']['input']['required']['sampler_name'][0]))"
```
