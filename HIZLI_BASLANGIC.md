# 🚀 Hızlı Başlangıç Rehberi

## Adım 1: LLM Sunucusunu Başlatın

1. `start_llm_server.ps1` dosyasına sağ tıklayıp **"PowerShell ile Çalıştır"** deyin veya terminalden çalıştırın.
2. Konsol penceresinde şu mesajı bekleyin:

   ```text
   listening on 127.0.0.1:8080
   ```

3. Bu pencereyi **KAPATMAYIN** (arka planda çalışmalı)

## Adım 2: Web Arayüzünü Başlatın

1. **Yeni bir terminal** açın veya `start_web_ui.ps1` dosyasını çalıştırın.
2. Tarayıcınızda otomatik olarak açılacak: `http://127.0.0.1:7861`
3. Açılmazsa manuel olarak bu adresi ziyaret edin

## Adım 3: PDF İle Çalışın

### PDF İndeksleme

1. "**PDF yükle (.pdf)**" butonuna tıklayın
2. PDF dosyanızı seçin
3. "**📥 PDF'yi İndeksle**" butonuna tıklayın
4. İndeksleme tamamlanınca durum mesajı görünecek

### Soru Sorma

1. Sohbet kutusuna sorunuzu yazın
   - Örnek: "Bu belgede hangi konular ele alınıyor?"
   - Örnek: "Önerilen yöntem nedir?"
2. Enter'a basın veya gönder butonuna tıklayın
3. AI cevabı oluşturacak (birkaç saniye sürebilir)

### Özet Alma

1. "**Özet madde sayısı**" slider'ını ayarlayın (3-10 arası)
2. "**📝 Kısa Özet Al**" butonuna tıklayın
3. Dokümanın kısa özeti görünecek

## Adım 4: İndeksi Temizleme

Yeni bir PDF ile başlamak için:

1. "**🧹 İndeksi Temizle**" butonuna tıklayın
2. Yeni PDF'inizi yükleyin ve indeksleyin

## ⚠️ Önemli Notlar

- **İlk çalıştırma** biraz yavaş olabilir (model yükleniyor)
- **GPU varsa** çok daha hızlı çalışır
- **İndekslenen PDF'ler** kalıcı olarak saklanır (`rag_store/` klasöründe)
- **Her iki pencereyi de** açık tutun (LLM sunucusu + Web UI)

## 🔧 Sorun mu var?

### "Connection refused" hatası

➡️ LLM sunucusunun çalıştığından emin olun (Adım 1)

### Türkçe karakterler bozuk

➡️ Terminal kodlamasını UTF-8'e ayarlayın: `chcp 65001`

### Çok yavaş çalışıyor

➡️ GPU sürücülerinizi güncelleyin veya `-ngl 0` ile CPU modunda çalıştırın

## 📞 Yardım

Daha fazla bilgi için `README.md` dosyasına bakın.

---

### İyi çalışmalar! 🎉
