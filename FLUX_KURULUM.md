# Flux Schnell Kurulum Rehberi

## Adım 1: HuggingFace Hesabı ve Token

### 1.1. HuggingFace Hesabı Oluştur (yoksa)
- https://huggingface.co/join adresine git
- Ücretsiz hesap oluştur

### 1.2. Access Token Oluştur
1. https://huggingface.co/settings/tokens adresine git
2. "New token" butonuna tıkla
3. Token adı gir (örn: "flux-download")
4. Type: **"Read"** seç (Write gerekmez)
5. "Generate token" butonuna tıkla
6. Token'ı **kopyala** (bir daha gösterilmeyecek!)

## Adım 2: Model Erişimi İste

1. https://huggingface.co/black-forest-labs/FLUX.1-schnell adresine git
2. "Agree and access repository" veya benzeri butona tıkla
3. Kullanım şartlarını kabul et
4. Erişim onayını bekle (genelde anında)

## Adım 3: HuggingFace CLI ile Giriş Yap

Terminal'de:

```bash
huggingface-cli login
```

Token'ınızı yapıştırın (görünmez ama yazılıyor) ve Enter'a basın.

Başarılı mesaj görmelisiniz:
```
Token is valid (permission: read).
Your token has been saved to /Users/tankucukhas/.cache/huggingface/token
```

## Adım 4: Flux Schnell'i İndir

### Seçenek A: HuggingFace CLI (Önerilen)

```bash
cd ~/Documents/ComfyUI/models/checkpoints/

huggingface-cli download black-forest-labs/FLUX.1-schnell \
  flux1-schnell.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False
```

Bu komut:
- ~23 GB dosyayı indirir
- Doğrudan checkpoints klasörüne kaydeder
- İlerleme gösterir

### Seçenek B: Python Script ile

```bash
cd ~/workspace/nudify
source venv/bin/activate
pip install huggingface-hub

python3 << 'EOF'
from huggingface_hub import hf_hub_download
import os

print("Flux Schnell indiriliyor...")
hf_hub_download(
    repo_id="black-forest-labs/FLUX.1-schnell",
    filename="flux1-schnell.safetensors",
    local_dir=os.path.expanduser("~/Documents/ComfyUI/models/checkpoints/"),
    local_dir_use_symlinks=False
)
print("✓ İndirme tamamlandı!")
EOF
```

### Seçenek C: Manuel Tarayıcı İndirme

1. https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/main
2. Giriş yap
3. "flux1-schnell.safetensors" (23.8 GB) dosyasına tıkla
4. "download" butonuna tıkla
5. İndirilen dosyayı `~/Documents/ComfyUI/models/checkpoints/` klasörüne taşı

## Adım 5: Doğrula

```bash
ls -lh ~/Documents/ComfyUI/models/checkpoints/flux1-schnell.safetensors
```

Çıktı şöyle olmalı:
```
-rw-r--r--  1 tankucukhas  staff    23G Nov 16 01:30 flux1-schnell.safetensors
```

## Adım 6: ComfyUI'de Test Et

1. ComfyUI'yi yeniden başlat (çalışıyorsa)
2. "Load Checkpoint" node'una tıkla
3. Dropdown'da "flux1-schnell.safetensors" görünmeli
4. Test görseli oluştur

## Sorun Giderme

### "Access denied" hatası
- Model sayfasında erişim iznini onayladığınızdan emin olun
- Token'ın "Read" yetkisi olduğundan emin olun
- `huggingface-cli whoami` ile giriş kontrolü yapın

### İndirme çok yavaş
- İnternet bağlantınızı kontrol edin
- Tarayıcı indirme seçeneğini deneyin
- Download manager kullanabilirsiniz (IDM, aria2c, vb.)

### "No space left on device"
- Disk alanını kontrol edin: `df -h`
- En az 25 GB boş alan gerekli
- Gerekirse başka disk kullanın

### Token hatası
- Token'ı doğru kopyaladığınızdan emin olun
- Yeni token oluşturup tekrar deneyin
- `rm ~/.cache/huggingface/token` ve yeniden giriş yapın

## Alternatif: Daha Küçük Modeller

Eğer 23 GB çok büyükse:

### SDXL Base (6.5 GB) - Zaten indirilmiş SDXL Lightning var
```bash
cd ~/Documents/ComfyUI/models/checkpoints/
curl -L -o sd_xl_base_1.0.safetensors \
  "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
```

### SD 1.5 (4 GB) - En küçük, hızlı testler için
```bash
curl -L -o sd_v1-5.safetensors \
  "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
```

## Özet Komutlar

```bash
# 1. Giriş yap
huggingface-cli login

# 2. İndir
cd ~/Documents/ComfyUI/models/checkpoints/
huggingface-cli download black-forest-labs/FLUX.1-schnell \
  flux1-schnell.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False

# 3. Doğrula
ls -lh flux1-schnell.safetensors
```

İndirme yaklaşık 5-15 dakika sürer (internet hızına bağlı).
