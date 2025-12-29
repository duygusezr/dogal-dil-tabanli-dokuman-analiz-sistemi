# 🐳 Docker ile Taşınabilir Kurulum Rehberi

Bu proje **tamamen taşınabilir** yapıdadır. Model dosyası dahil her şey paket içerisindedir.

## 📋 Gereksinimler

- **Docker Desktop** (Windows/Mac) veya **Docker Engine** (Linux)
- (Opsiyonel) NVIDIA Ekran Kartı sürücüsü (GPU kullanmak için)

---

## 🚀 Çalıştırma Adımları

Proje klasörü kodları içerir.

> ⚠️ **ÖNEMLİ: GitHub'dan İndirenler İçin**
>
> Yapay Zeka modeli (~4.5GB) dosya boyutu nedeniyle GitHub'da yüklü değildir. Projeyi indirdikten sonra modeli manuel olarak eklemelisiniz:
>
> 1. Modeli indirin: [Buraya Tıklayın (HuggingFace)](https://huggingface.co/matrixportalx/Turkish-Llama-8b-Instruct-v0.1-GGUF/resolve/main/Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf?download=true)
> 2. İndirdiğiniz dosyanın adının tam olarak şu olduğundan emin olun:  
>     `Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf`
> 3. Dosyayı şuraya taşıyın:
>     `models/turkish/`
>
> Eğer bu klasörler yoksa oluşturun. Sonuç şöyle görünmeli:
> `Proje/models/turkish/Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf`

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

## 🔄 Sistemi Durdurma

Sistemi kapatmak için:

**Windows:**

```powershell
docker_durdur.ps1
```

**Terminal (Evrensel):**

```bash
docker-compose down
```

---

## ❓ Sıkça Sorulan Sorular

**Soru: Python kurmam gerekiyor mu?**
**Cevap:** Hayır! Docker kullanıyorsanız sadece Docker Desktop yeterlidir. Python, Tesseract ve tüm bağımlılıklar container içinde hazır gelir.

**Soru: Modeli indirmem gerekiyor mu?**
**Cevap:** Evet, GitHub'dan indirdiyseniz. Model dosyası (~4.5GB) boyut sınırı nedeniyle GitHub'a yüklenmemiştir. Yukarıdaki "ÖNEMLİ" bölümünden indirin.

**Soru: Başka bilgisayara nasıl taşırım?**
**Cevap:**

1. Modeli indirip `models/turkish/` klasörüne koyun
2. Tüm proje klasörünü kopyalayın (USB, ZIP vb.)
3. Hedef bilgisayarda Docker Desktop'ı çalıştırın
4. `docker_baslat.ps1` veya `docker-compose up` komutunu çalıştırın

**Soru: GPU'm yoksa ne olur?**
**Cevap:** Sistem otomatik olarak CPU moduna geçer, ancak cevap verme süresi uzayabilir (GPU: ~2sn, CPU: ~30sn).

**Soru: İlk çalıştırmada neden yavaş?**
**Cevap:** Docker, gerekli imajları (llama.cpp, Python vb.) internetten indiriyor. İlk kurulum 5-10 dakika sürebilir. Sonraki çalıştırmalar anlık olacaktır.
