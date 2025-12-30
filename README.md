# 🤖 Türkçe LLM + RAG Doküman Analiz Sistemi

Bu proje, yerel olarak çalışan yapay zeka destekli bir doküman analiz sistemidir. Türkçe PDF dokümanlarını okur, içeriğini anlar ve sorduğunuz sorulara doküman içeriğine sadık kalarak cevap verir.

## Öne Çıkan Özellikler

- **🔒 %100 Gizlilik:** İnternet gerektirmez, verileriniz bilgisayarınızdan dışarı çıkmaz.
- **🐳 Tam Taşınabilir (Docker):** Python, CUDA vs. kurmakla uğraşmazsınız. Tek komutla çalışır.
- **📄 OCR Desteği:** Resim formatındaki (taranmış) PDF'leri de okuyabilir.
- **🧠 Akıllı RAG:** Büyük dokümanları parçalar, sadece ilgili kısımları kullanarak cevap üretir.

---

## 🛠️ Gereksinimler

1. **Docker Desktop** (Yüklü ve çalışıyor olmalı)
2. **(İsteğe Bağlı) NVIDIA Ekran Kartı:** Cevapların hızlı üretilmesi için önerilir. Yoksa işlemci (CPU) kullanılır.

---

## 🚀 Kurulum (Adım Adım)

### Adım 1: Modeli İndirin

GitHub dosya boyutu sınırı nedeniyle AI modeli projeye dahil değildir. Modeli bir kez indirip yerine koymanız gerekir.

1. Modeli şu linkten indirin (~4.5 GB):
    👉 [**Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf**](https://huggingface.co/matrixportalx/Turkish-Llama-8b-Instruct-v0.1-GGUF/resolve/main/Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf?download=true)
2. İndirdiğiniz dosyayı proje içindeki şu yola koyun:
    `models/Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf`

> **Not:** `models` klasörü yoksa oluşturun. Klasör yapısı tam olarak şöyle olmalı:
> `Proje -> models -> Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf`

### Adım 2: Sistemi Başlatın

Sadece şu komutu çalıştırın:

```powershell
docker-compose up --build
```

> *(İlk çalıştırmada gerekli dosyaları indireceği için 5-10 dakika sürebilir. Sonrakilerde hemen açılır.)*

---

## 🖥️ Kullanım

Sistem açıldığında terminalde loglar akmaya başlar.

1. Tarayıcınızı açın ve şu adrese gidin:
    👉 **<http://localhost:7861>**
2. **"PDF Yükle"** butonuna basarak bir doküman seçin.
3. **"📥 PDF’yi İndeksle"** butonuna basın. (Log ekranında "İndeksleme Tamam" yazısını bekleyin).
4. Aşağıdaki sohbet kutusuna sorunuzu yazın.

### Örnek Sorular

- "Bu belgenin ana fikri nedir?"
- "Sözleşmedeki ceza koşulları nelerdir?"
- "Rapora göre 2023 yılı kârı ne kadar?"

> **İpucu:** Cevapların uzunluğu veya kısalığı için "Özet Madde Sayısı" ayarını kullanabilirsiniz.

---

## ❓ Sorun Giderme

- **"docker-compose command not found" hatası:** Docker Desktop'ın kurulu olduğundan emin olun.
- **Web sitesi açılmıyor:** Terminalde `Running on local URL:  http://0.0.0.0:7861` yazısını görene kadar bekleyin.
- **Sistemi kapatmak için:** Terminal ekranında `Ctrl + C` tuşlarına basın.
- **Sistemi sıfırlamak için:** İndekslenen belgeleri temizlemek isterseniz `rag_store` klasörünü silebilirsiniz veya arayüzden "İndeksi Temizle" diyebilirsiniz.

---

## 📂 Dosya Yapısı

```text
Proje/
├── models/             # İndirdiğiniz AI Modeli (GGUF)
├── rag_store/          # Vektör veritabanı (Otomatik oluşur)
├── app_rag.py          # Python uygulama kodu
├── docker-compose.yml  # Servis ayarları
├── Dockerfile          # Web arayüzü imaj ayarları
├── requirements.txt    # Kütüphane listesi
└── README.md           # Bu dosya
```
