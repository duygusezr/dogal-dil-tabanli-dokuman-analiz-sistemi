# 📖 Örnek Kullanım Senaryoları

## Senaryo 1: Akademik Makale Analizi

### S1 - Adım 1: PDF Yükleme

1. Akademik makalenizi (örn: `arastirma_makalesi.pdf`) yükleyin
2. "📥 PDF'yi İndeksle" butonuna tıklayın

### S1 - Adım 2: Soru Örnekleri

```text
❓ Bu makalede hangi araştırma sorusu ele alınıyor?
❓ Kullanılan yöntem nedir?
❓ Araştırmanın ana bulguları nelerdir?
❓ Hangi veri seti kullanılmış?
❓ Gelecek çalışmalar için öneriler neler?
```

### S1 - Adım 3: Özet Alma

- Madde sayısı: 5-7
- "📝 Kısa Özet Al" ile makalenin özetini alın

---

## Senaryo 2: Teknik Dokümantasyon

### S2 - Kullanım Soruları

```text
❓ Bu sistemin kurulum adımları nelerdir?
❓ Hangi bağımlılıklar gereklidir?
❓ Konfigürasyon parametreleri nelerdir?
❓ Sorun giderme için öneriler neler?
```

---

## Senaryo 3: Yasal Belge İnceleme

### S3 - Kullanım Soruları

```text
❓ Bu sözleşmenin ana maddeleri nelerdir?
❓ Tarafların yükümlülükleri neler?
❓ Fesih koşulları nelerdir?
❓ Ödeme şartları nasıl düzenlenmiş?
```

---

## Senaryo 4: Eğitim Materyali

### S4 - Kullanım Soruları

```text
❓ Bu konuda hangi kavramlar açıklanıyor?
❓ Örnekler nelerdir?
❓ Önemli formüller hangileri?
❓ Pratik uygulamalar neler?
```

---

## 💡 İpuçları

### Etkili Soru Sorma

- ✅ **Spesifik olun**: "Yöntem nedir?" yerine "Hangi makine öğrenmesi yöntemi kullanılmış?"
- ✅ **Bağlam verin**: "2. bölümde bahsedilen..."
- ✅ **Açık uçlu sorular**: "Neden?", "Nasıl?", "Nelerdir?"
- ❌ **Kapalı sorular**: "Evet/Hayır" soruları yerine detay isteyin

### Özet Alma Hakkında

- **3-5 madde**: Hızlı genel bakış
- **5-7 madde**: Dengeli özet
- **8-10 madde**: Detaylı özet

### Performans İyileştirme

- **Küçük PDF'ler**: Daha hızlı indeksleme
- **Temiz metin**: OCR gerektirmeyen PDF'ler tercih edin
- **İndeksi temizleyin**: Gereksiz dokümanları kaldırın

---

## 🎯 Test Dokümanı

Proje klasöründe `test_dokuman.pdf` adında bir test dosyası bulunmaktadır.

### Test Soruları

```text
❓ Yapay zeka nedir?
❓ Makine öğrenmesi hangi alanları içerir?
❓ Derin öğrenme nedir?
❓ Yapay zeka hangi alanlarda kullanılıyor?
❓ Türkiye'de yapay zeka çalışmaları nasıl?
```

### Beklenen Özet (5 madde)

1. Yapay zeka, bilgisayar sistemlerinin insan zekasını taklit etmesidir
2. Makine öğrenmesi, sistemlerin deneyimlerden öğrenmesini sağlar
3. Derin öğrenme, yapay sinir ağları kullanarak karmaşık problemleri çözer
4. Doğal dil işleme, görüntü tanıma, otonom araçlar gibi alanlarda kullanılır
5. Türkiye'de üniversiteler ve araştırma merkezleri önemli projeler yürütmektedir

---

## 🔄 Çoklu Doküman Çalışması

### Yöntem 1: Sıralı İndeksleme

1. İlk PDF'yi yükle ve indeksle
2. İkinci PDF'yi yükle ve indeksle
3. Tüm dokümanlar aynı vektör DB'de saklanır
4. Sorular tüm dokümanlarda aranır

### Yöntem 2: Temiz Başlangıç

1. "🧹 İndeksi Temizle" ile baştan başla
2. Yeni PDF'yi yükle
3. Sadece o doküman üzerinde çalış

---

## 📊 Örnek Çıktılar

### Örnek Soru

```text
❓ Yapay zeka hangi alanlarda kullanılıyor?
```

### Beklenen Cevap

```text
Bağlama göre, yapay zeka şu alanlarda kullanılmaktadır:
- Doğal dil işleme
- Görüntü tanıma
- Otonom araçlar
- Sağlık teşhisi
- Finansal analiz

[Kaynak: test_dokuman.pdf | Parça: 2]
```

---

## 🚀 İleri Seviye Kullanım

### Parametre Ayarlama (app_rag.py)

```python
# Daha fazla bağlam için
TOP_K = 10  # Varsayılan: 6

# Daha uzun cevaplar için
MAX_ANSWER_TOKENS = 1000  # Varsayılan: 700

# Daha büyük parçalar için
CHUNK_SIZE = 1500  # Varsayılan: 1000
```

### LLM Sunucu Ayarları (start_llm_server.ps1)

```powershell
# Daha fazla context için
-c 16384  # Varsayılan: 8192

# Daha fazla thread için
-t 16  # Varsayılan: 12

# CPU modunda çalıştırma
-ngl 0  # Varsayılan: 999 (GPU)
```

---

### **Başarılı kullanımlar! 🎉**
