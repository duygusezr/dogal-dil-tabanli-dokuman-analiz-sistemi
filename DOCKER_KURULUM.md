# 🐳 Docker ile Taşınabilir Kurulum Rehberi

Bu proje **tamamen taşınabilir** yapıdadır. Model dosyası dahil her şey paket içerisindedir.

## 📋 Gereksinimler

- **Docker Desktop** (Windows/Mac) veya **Docker Engine** (Linux)
- (Opsiyonel) NVIDIA Ekran Kartı sürücüsü (GPU kullanmak için)

---

## 🚀 Çalıştırma Adımları

Proje klasörü ihtiyacınız olan her şeyi içerir. Model dosyası `models/turkish/` dizininde hazırdır.

### Kolay Başlatma (Windows)

1. `docker_baslat.ps1` dosyasına sağ tıklayın.
2. "PowerShell ile Çalıştır" seçeneğini seçin.

### Terminal ile Başlatma (Evrensel)

Terminal veya PowerShell'i proje klasöründe açın ve:

```text
docker-compose up --build
```

### Erişim Bilgileri

- **Web Arayüzü**: `http://localhost:7861`
- **RAG API**: `http://localhost:8080`

---

## 📂 Proje Yapısı

```text
Proje Klasörü/
├── app_rag.py                 # RAG Uygulaması
├── docker-compose.yml         # Konteyner ayarları (Taşınabilir yol ayarlı)
├── Dockerfile                 # İmaj tarifi
├── models/                    # ✨ LLM Modeli burada
│   └── turkish/
│       └── Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf
├── rag_store/                 # Veritabanı (Çalışınca oluşur)
└── ... (Yardımcı scriptler)
```

## ❓ Sıkça Sorulan Sorular

**Soru: Modeli indirmem gerekiyor mu?**
**Cevap:** Hayır, model dosyası proje klasörüne dahil edilmiştir.

**Soru: Başka bilgisayara nasıl taşırım?**
**Cevap:** Tüm proje klasörünü (USB bellek, ZIP vb. ile) kopyalamanız yeterlidir.

**Soru: GPU'm yoksa ne olur?**
**Cevap:** Sistem otomatik olarak CPU moduna geçer, ancak cevap verme süresi uzayabilir.
