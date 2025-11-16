# Changelog

Tüm önemli değişiklikler bu dosyada belgelenmiştir.

## [1.0.0] - 2024-11-16

### 🎉 İlk Sürüm

Tam işlevsel AI görsel üretim lab'ı oluşturuldu.

### ✨ Eklenenler

#### Temel Yapı
- **Proje yapısı** oluşturuldu (backend/, configs/, scripts/, workflows/)
- **Python 3.13 sanal ortamı** kuruldu
- **Tüm bağımlılıklar** yüklendi (FastAPI, Pydantic, requests, etc.)

#### Backend Sistemi
- **FastAPI server** (`backend/server.py`)
  - `/generate` endpoint - Görsel üretimi
  - `/health` endpoint - Sistem sağlık kontrolü
  - Otomatik API dokümantasyonu (/docs)
- **ComfyUI client** (`backend/comfyui_client.py`)
  - ComfyUI API entegrasyonu
  - Workflow oluşturma ve yönetimi
  - Görsel kaydetme ve metadata yönetimi
- **Pydantic modeller** (`backend/models.py`)
  - Request/Response doğrulama
  - Tip güvenliği

#### Konfigürasyon Sistemi
- **JSON Schema** (`configs/schema.json`) - Deneyim doğrulama
- **Base prompts** (`configs/base_prompt.json`) - Prompt şablonları
- **Stage configs** (`configs/stages/`)
  - `pose.json` - İlk kompozisyon
  - `anatomy.json` - Anatomi iyileştirme
  - `lighting.json` - Işıklandırma
  - `detail.json` - Detay geliştirme
- **Örnek deneyim** (`configs/exp001_params.json`)

#### Scriptler ve Araçlar
- **run_experiments.py** - Ana deneyim runner'ı
  - Config yükleme ve doğrulama
  - Toplu deneyim çalıştırma
  - Sonuç kaydetme
- **eval_with_claude.py** - Claude değerlendirme
  - Vision API entegrasyonu
  - Otomatik skorlama (pose, anatomy, lighting, realism)
- **test_api.py** - API test scripti
- **Yardımcı shell scriptleri:**
  - `quick_start.sh` - Hızlı başlatma
  - `run_experiment.sh` - Deneyim çalıştırma
  - `check_status.sh` - Sistem kontrolü
  - `comfyui_baslat.sh` - ComfyUI başlatıcı
  - `restart_all.sh` - Tüm servisleri yeniden başlat
  - `download_models.sh` - Model indirme

#### Model Desteği
- **Flux Schnell** (22 GB) - Tam model, yüksek kalite
- **SDXL Base** (6.5 GB) - Kaliteli çıktı
- **SDXL Lightning** (4.8 GB) - Hızlı iterasyon
- Model mapping ve otomatik yükleme

#### Claude Entegrasyonu
- **Değerlendirme promptları** (`claude/prompts/`)
  - `evaluate_images.md` - Görsel değerlendirme
  - `generate_params.md` - Parametre önerileri
- Mock değerlendirme modu (API key olmadan)

#### Dokümantasyon
- **README_FULL.md** - Kapsamlı kullanım kılavuzu
- **CLAUDE.md** - Claude Code için rehber
- **MODELS.md** - Model kurulum detayları
- **FLUX_KURULUM.md** - Flux indirme adımları
- **NASIL_CALISTIRILIIR.md** - Adım adım kullanım
- **HATA_COZUMU.md** - Sorun giderme
- **SAMPLER_ISIMLERI.md** - Scheduler referansı
- **KURULUM_TAMAMLANDI.md** - Kurulum özeti
- **DURUM.md** - Sistem durumu

#### Environment ve Config
- **`.env.example`** - Environment değişken şablonu
- **`.env`** - Yerel konfigürasyon (gitignore'da)
- **`.gitignore`** - Kapsamlı ignore kuralları
- **`requirements.txt`** - Python bağımlılıkları
- **`Makefile`** - Hızlı komutlar

### 🔧 Düzeltmeler

#### Port Çakışmaları
- ComfyUI port 8000'de çalışıyor tespit edildi
- Backend port 8001'e taşındı
- `.env` dosyası ile port yönetimi eklendi

#### Scheduler İsimleri
- `euler_a` → `euler` (ComfyUI uyumluluğu)
- Geçerli scheduler listesi eklendi
- Config dosyaları güncellendi

#### Model Uyumluluk
- SDXL Lightning'in sadece UNet içerdiği tespit edildi
- SDXL Base eklenmesi gerektiği dokümante edildi
- Flux Schnell tam model olarak önerildi
- Model mapping'i düzeltildi

### 🚀 İyileştirmeler

#### Developer Experience
- Otomatik sistem kontrolü scriptleri
- Renkli terminal çıktıları
- Detaylı hata mesajları
- İlerleme göstergeleri

#### API
- Otomatik health check
- Detaylı metadata tracking
- Hata yakalama ve loglama
- API dokümantasyon (FastAPI docs)

#### Workflow
- Tek komutla başlatma
- Otomatik doğrulama
- Dry-run modu
- Sonuç görüntüleme

### 📦 Kurulum Değişiklikleri

#### HuggingFace Entegrasyonu
- Token tabanlı kimlik doğrulama
- `huggingface-cli` kullanımı
- Model erişim yönetimi

#### Python Environment
- Python 3.13 desteği
- Flexible versiyon requirements
- Pydantic v2 uyumluluğu

### 🐛 Bilinen Sorunlar

- SDXL Lightning tek başına çalışmıyor (SDXL Base gerekli)
- ComfyUI varsayılan port 8000 kullanıyor (8188 yerine)
- İlk başlatma yavaş olabiliyor (model tarama)

### 📝 Notlar

- **Platform:** macOS (Apple Silicon optimize)
- **Python:** 3.13+
- **ComfyUI:** Desktop version
- **Total Size:** ~30 GB (modeller dahil)

### 🔜 Gelecek Planlar

- [ ] Docker support (Linux 3090 deployment)
- [ ] n8n orchestration entegrasyonu
- [ ] Gerçek Claude API implementasyonu
- [ ] Batch processing iyileştirmeleri
- [ ] Web UI (opsiyonel)
- [ ] Model caching optimizasyonu
- [ ] ControlNet desteği
- [ ] LoRA desteği

---

## Katkıda Bulunanlar

- Claude Code (AI Assistant) - Tüm kod ve dokümantasyon
- @tankucukhas - Proje sahibi ve test

## Değişiklik Tipi İşaretleri

- 🎉 İlk sürüm
- ✨ Yeni özellik
- 🔧 Düzeltme
- 🚀 İyileştirme
- 📦 Bağımlılık
- 🐛 Bug fix
- 📝 Dokümantasyon
- 🔜 Gelecek
