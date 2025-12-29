# 🤖 Türkçe LLM + RAG Doküman Analiz Sistemi

Bu proje, **Turkish-Llama-8b** modeli kullanarak Türkçe PDF dokümanları üzerinde RAG (Retrieval-Augmented Generation) tabanlı soru-cevap sistemi sağlar.

✅ **Tam Taşınabilir:** Docker sayesinde model dahil her şeyiyle tak-çalıştır yapısındadır.
✅ **OCR Destekli:** Taranmış (resim) PDF'leri okuyabilir.

## 📁 Paket İçeriği

- **Model**: Turkish-Llama-8b-Instruct-v0.1 (~5GB) *(⚠️ GitHub sürümüne dahil değildir, ayrıca indirilmelidir)*
- **Uygulama**: Web Arayüzü (Gradio)
- **Veritabanı**: Vektör DB (ChromaDB)
- **Araçlar**: OCR (Tesseract), PDF Okuyucu

## ⚠️ Önemli: Model Kurulumu

GitHub'dan indirenler için model dosyası dahil değildir. Kuruluma başlamadan önce:

1. [Modeli İndir (HuggingFace)](https://huggingface.co/matrixportalx/Turkish-Llama-8b-Instruct-v0.1-GGUF/resolve/main/Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf?download=true)
2. `models/turkish/` klasörü oluşturup içine atın.
3. Dosya adının `Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf` olduğundan emin olun.

## 🚀 Nasıl Çalıştırılır?

Bu paket iki şekilde çalıştırılabilir.

### Seçenek 1: Docker ile (Önerilen) 🐳

En kolay ve sorunsuz yöntemdir. Başka bilgisayarlara taşınabilir.
[Detaylı Docker Rehberi için Tıklayın](DOCKER_KURULUM.md)

1. `docker_baslat.ps1` dosyasına sağ tıklayın.
2. **"PowerShell ile Çalıştır"** diyerek başlatın.
3. Tarayıcıda `http://localhost:7861` adresine gidin.

### Seçenek 2: Yerel Kurulum (Gelişmiş) 🛠️

Kendi bilgisayarınızda Python, CUDA vb. kurarak çalıştırmak isterseniz:

1. `start_llm_server.ps1` ile sunucuyu başlatın.
2. `start_web_ui.ps1` ile arayüzü başlatın.

## ⚙️ Özellikler

- **GPU Hızlandırma**: NVIDIA GPU varsa otomatik kullanır.
- **Akıllı OCR**: Metin içermeyen sayfaları otomatik algılar ve okur.
- **Kalıcı Hafıza**: Yüklediğiniz dokümanlar silinmez, `rag_store` klasöründe saklanır.
- **Türkçe Odaklı**: Model ve promptlar Türkçe için optimize edilmiştir.

## 🔍 Sorun Giderme

- **Docker açılmıyor**: Docker Desktop uygulamasının açık olduğundan emin olun.
- **Yavaş çalışıyor**: GPU yoksa sistem CPU kullanır, cevaplar yavaşlayabilir.
- **Kapatma**: `docker_durdur.ps1` dosyasını çalıştırarak sistemi kapatabilirsiniz.

## 📂 Dosya Yapısı

```text
Proje/
├── models/                    # Dahili Model Dosyası
├── app_rag.py                 # Kaynak Kod
├── docker-compose.yml         # Docker Ayarları
├── DOCKER_KURULUM.md          # Kurulum Rehberi
├── SIFIR_BILGI_KILAVUZU.md    # Basit Rehber
└── ... (Başlatıcı Scriptler)
```

---

**İyi çalışmalar!** 🚀
