import os, gradio as gr, fitz, re, time, csv, datetime
from openai import OpenAI
import pytesseract
from PIL import Image, ImageEnhance

# ---- Ayarlar ve Yollar ----
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# ---- LLM: yerel llama-server (OpenAI uyumlu) ----
llm_api_url = os.getenv("LLM_API_URL", "http://127.0.0.1:8080/v1")
client = OpenAI(api_key="local", base_url=llm_api_url)

# ---- Vektör veritabanı & embedding ----
import chromadb
from chromadb.config import Settings
from fastembed import TextEmbedding

# FastEmbed desteklenen model (Türkçe için de çalışır)
EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # ✅ FastEmbed tarafından destekleniyor
# Alternatifler:
# "sentence-transformers/all-MiniLM-L6-v2" - Daha hızlı
# "BAAI/bge-base-en-v1.5" - Daha güçlü ama yavaş

# Optimize edilmiş parametreler - 🔥 OCR için GEVŞEK ayarlar
CHUNK_SIZE = 600  # Daha küçük = daha spesifik eşleşme
CHUNK_OVERLAP = 250  # 🔥 Artırıldı: Daha fazla overlap = daha iyi bağlam
TOP_K = 8  # DAHA FAZLA kaynak = daha iyi şans
MAX_ANSWER_TOKENS = 2000
SIMILARITY_THRESHOLD = 0.35  # 🔥 DÜŞÜRÜLDÜ: OCR hatalarına toleranslı (0.40 → 0.35)

PERSIST_DIR = "./rag_store"
COLLECTION_NAME = "pdf_chunks"

embedder = TextEmbedding(model_name=EMBED_MODEL)

db = chromadb.PersistentClient(path=PERSIST_DIR, settings=Settings(allow_reset=True))
try:
    col = db.get_collection(COLLECTION_NAME)
except:
    col = db.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

# ---- GELİŞTİRİLMİŞ SYSTEM PROMPT ----
SYSTEM_RAG = """Sen bir doküman analiz asistanısın.

GÖREV: Verilen BAĞLAM'ı kullanarak soruyu cevapla.

KURALLAR:
- BAĞLAM'da cevap varsa → Dokümandaki bilgiyi kullanarak cevapla
- BAĞLAM'da cevap yoksa → "Bu bilgi dokümanda bulunmuyor" de
- Cevaplarını Türkçe, net ve anlaşılır yaz

ÖNEMLİ: Sadece verilen BAĞLAM'ı kullan. Kendi genel bilgini ekleme."""

def ocr_page(page_pixmap):
    """Geliştirilmiş OCR - contrast ve denoise ile"""
    try:
        img = Image.frombytes("RGB", [page_pixmap.width, page_pixmap.height], page_pixmap.samples)
        
        # Görüntüyü büyüt (daha iyi OCR için)
        img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
        
        # Griye çevir
        img = img.convert('L')
        
        # Kontrast artır (OCR için daha iyi)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)
        
        # Parlaklık artır
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        
        # Keskinlik artır
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # OCR config - Türkçe için optimize (PSM 3 = tam sayfa)
        custom_config = r'--oem 3 --psm 3 -l tur'
        text = pytesseract.image_to_string(img, config=custom_config)
        
        return text
    except Exception as e:
        print(f"OCR Hatası: {e}")
        return ""

def _read_pdf(path):
    """PDF okuma - metin + OCR fallback"""
    doc = fitz.open(path)
    parts = []
    
    print(f"📄 PDF Analiz ediliyor: {path}")
    print(f"   Toplam sayfa sayısı: {len(doc)}")
    
    for i, page in enumerate(doc):
        txt = page.get_text("text")
        
        # Metin varsa kontrol et - ama çok az veya garip karakterler varsa OCR dene
        text_length = len(txt.strip())
        
        print(f"\n   📄 Sayfa {i+1}:")
        print(f"      Metin çıkarma: {text_length} karakter")
        
        # Eğer metin çok azsa veya %80'den fazlası sayı/özel karakter ise OCR dene
        should_ocr = False
        if text_length < 50:
            should_ocr = True
            print(f"      ⚠️ Metin çok az, OCR gerekli")
        elif text_length < 200:
            # Metin var ama az - belki düzgün değil, OCR'ı da dene
            alphanum = sum(c.isalnum() for c in txt)
            if alphanum / len(txt) < 0.5:  # %50'den az alfanumerik karakter
                should_ocr = True
                print(f"      ⚠️ Metin kalitesiz (%{int(alphanum/len(txt)*100)} alfanumerik), OCR gerekli")
        
        if should_ocr:
            print(f"      🔄 OCR işlemi başlıyor (DPI: 400)...")
            try:
                # Yüksek çözünürlük (DPI 400)
                pix = page.get_pixmap(dpi=400)
                ocr_txt = ocr_page(pix)
                ocr_length = len(ocr_txt.strip())
                
                print(f"      📝 OCR sonucu: {ocr_length} karakter")
                
                if ocr_txt and ocr_length > text_length:
                    txt = ocr_txt
                    print(f"      ✅ OCR kullanıldı ({ocr_length} > {text_length})")
                    
                    # İlk 200 karakteri göster (debug için)
                    preview = ocr_txt[:200].replace('\n', ' ')
                    print(f"      👁️ Önizleme: {preview}...")
                else:
                    print(f"      ⚠️ OCR sonucu kötü, orijinal metin kullanılıyor")
            except Exception as e:
                print(f"      ❌ OCR hatası: {e}")
        else:
            print(f"      ✅ Metin yeterli ({text_length} karakter)")
            # İlk 200 karakteri göster
            preview = txt[:200].replace('\n', ' ')
            print(f"      👁️ Önizleme: {preview}...")
        
        if txt and txt.strip():
            parts.append(txt)
        else:
            print(f"      ⚠️ Bu sayfa boş, atlanıyor")
            
    full_text = "\n".join(parts)
    print(f"\n✅ TOPLAM: {len(full_text)} karakter, {len(parts)} sayfa işlendi")
    
    if len(full_text) < 100:
        print("⚠️ UYARI: Çok az metin çıkarıldı! OCR ayarlarını kontrol edin.")
    
    return full_text

def _chunkify_smart(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Akıllı parçalama - cümle sınırlarına göre"""
    # Cümlelere böl (Türkçe noktalama)
    sentences = re.split(r'(?<=[.!?;:])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sent in sentences:
        # Boş cümleleri atla
        if not sent.strip():
            continue
            
        # Eğer bu cümleyi ekleyince boyut aşılırsa
        if len(current_chunk) + len(sent) + 1 > size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sent + " "
        else:
            current_chunk += sent + " "
    
    # Son chunk'ı ekle
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Overlap ekle (son N kelimeyi bir sonraki chunk'a taşı)
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_words = chunks[i-1].split()
            overlap_words = prev_words[-min(overlap//5, len(prev_words)):]  # Kelime bazlı overlap
            overlapped.append(" ".join(overlap_words) + " " + chunks[i])
        return overlapped
    
    return chunks

def index_pdf(file):
    """PDF'yi indeksle - geliştirilmiş feedback"""
    if not file:
        return "⚠️ Önce bir PDF dosyası seçin."
    
    try:
        text = _read_pdf(file.name)
        
        if not text.strip():
            return "❌ PDF'den metin çıkarılamadı. OCR desteği aktif mi kontrol edin."
        
        # Akıllı chunking
        chunks = _chunkify_smart(text, CHUNK_SIZE, CHUNK_OVERLAP)
        
        if not chunks:
            return "❌ Metin parçalanamadı."
        
        # Embedding oluştur
        print(f"🔄 {len(chunks)} parça için embedding oluşturuluyor...")
        ids = [f"{os.path.basename(file.name)}::{i}" for i in range(len(chunks))]
        embs = list(embedder.embed(chunks))
        
        # Zaman damgası ekle
        current_time = time.time()
        
        # ChromaDB'ye ekle
        col.add(
            ids=ids,
            documents=chunks,
            embeddings=embs,
            metadatas=[{
                "source": os.path.basename(file.name), 
                "chunk": i,
                "length": len(chunks[i]),
                "timestamp": current_time
            } for i in range(len(chunks))]
        )
        
        # İstatistikler
        avg_len = sum(len(c) for c in chunks) / len(chunks)
        return f"""✅ İndeksleme Başarılı!
        
📊 İstatistikler:
• Dosya: {os.path.basename(file.name)}
• Toplam Metin: {len(text):,} karakter
• Parça Sayısı: {len(chunks)}
• Ortalama Parça Boyutu: {int(avg_len)} karakter
• Embedding Modeli: {EMBED_MODEL}

Artık soru sorabilirsiniz! 💬"""
        
    except Exception as e:
        return f"❌ Hata oluştu: {str(e)}"

def clear_index():
    """Son yüklenen PDF'yi sil (Zaman damgasına göre en son)"""
    global col
    try:
        all_data = col.get(include=["metadatas"])
        
        if not all_data or not all_data["metadatas"]:
            return "⚠️ Silinecek belge yok."
        
        # Dosyaları ve zaman damgalarını topla
        file_timestamps = {}
        source_ids = {}
        
        for i, meta in enumerate(all_data["metadatas"]):
            source = meta.get("source", "unknown")
            timestamp = meta.get("timestamp", 0)
            
            # ID'leri kaydet
            if source not in source_ids:
                source_ids[source] = []
            source_ids[source].append(all_data["ids"][i])
            
            # En güncel timestamp'i bul
            if source not in file_timestamps:
                file_timestamps[source] = timestamp
            else:
                file_timestamps[source] = max(file_timestamps[source], timestamp)
        
        if not file_timestamps:
            return "⚠️ Silinecek belge yok."
        
        # En son eklenen dosyayı bul
        last_source = max(file_timestamps, key=file_timestamps.get)
        ids_to_delete = source_ids[last_source]
        
        # Kalan dosya sayısı
        remaining_count = len(file_timestamps) - 1
        
        # Silme işlemi
        col.delete(ids=ids_to_delete)
        
        return f"""🗑️ Son yüklenen PDF silindi!
        
📊 Silinen:
• Dosya: {last_source}
• Parça sayısı: {len(ids_to_delete)}

📚 Kalan dosya sayısı: {remaining_count}

💡 Tüm indeksi silmek için "Tüm İndeksi Sil" butonunu kullanın."""
        
    except Exception as e:
        import traceback
        return f"❌ Temizleme hatası: {str(e)}\n{traceback.format_exc()}"

def clear_all_index():
    """TÜM indeksi temizle - db.reset() kullanarak"""
    global col
    try:
        # Reset ile veri tabanını sıfırla
        db.reset()
        
        # Koleksiyonu tekrar oluştur
        col = db.get_or_create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
        
        return f"""🧹 TÜM İNDEKS VE VERİTABANI SIFIRLANDI!
        
⚠️ Bilgi:
"rag_store" klasörü diskte görünmeye devam edebilir, çünkü uygulama çalıştığı sürece veritabanı bağlantısı aktiftir. 
Ancak içi tamamen boştur ve tüm veriler silinmiştir.

✅ Veritabanı tertemiz!

🎯 Yeni PDF yükleyebilirsiniz."""
        
    except Exception as e:
        import traceback
        return f"❌ Temizleme hatası: {str(e)}\n{traceback.format_exc()}"

def log_to_csv(question, answer):
    """Soru ve cevabı CSV dosyasına kaydeder"""
    try:
        if not os.path.exists(PERSIST_DIR):
            os.makedirs(PERSIST_DIR)
            
        log_file = os.path.join(PERSIST_DIR, "chat_history.csv")
        file_exists = os.path.exists(log_file)
        
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Zaman", "Soru", "Cevap"])
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, question, answer])
            print(f"💾 Sohbet kaydedildi: {timestamp}")
    except Exception as e:
        print(f"❌ Log hatası: {e}")

def retrieve(question, top_k=TOP_K, show_scores=True):
    """Geliştirilmiş retrieval - skor bazlı filtreleme"""
    if not question.strip():
        return []
    
    try:
        print(f"\n🔍 RETRIEVAL: '{question}'")
        
        # Soru embedding
        qv = list(embedder.embed([question]))[0]
        print(f"   ✅ Soru embedding oluşturuldu (boyut: {len(qv)})")
        
        # Daha fazla sonuç al, sonra filtrele
        res = col.query(
            query_embeddings=[qv], 
            n_results=min(top_k * 3, 20),  # 3x al, en iyileri seç
            include=["documents", "metadatas", "distances"]
        )
        
        if not res or not res.get("documents") or not res["documents"][0]:
            print("   ⚠️ Hiç sonuç bulunamadı!")
            return []
        
        print(f"   📊 {len(res['documents'][0])} sonuç bulundu")
        
        ctxs = []
        for d, m, dist in zip(
            res["documents"][0], 
            res["metadatas"][0],
            res["distances"][0]
        ):
            # Cosine distance'ı similarity score'a çevir (0-1)
            similarity = 1 - (dist / 2)
            
            print(f"      • Benzerlik: {similarity:.2%} | Kaynak: {m.get('source', '?')} #{m.get('chunk', '?')}")
            
            # Threshold kontrolü
            if similarity >= SIMILARITY_THRESHOLD:
                ctxs.append({
                    "text": d,
                    "source": m.get("source", "?"),
                    "chunk": m.get("chunk", "?"),
                    "score": similarity,
                    "length": m.get("length", len(d))
                })
                print(f"        ✅ Eşik geçildi (%{SIMILARITY_THRESHOLD*100:.0f})")
            else:
                print(f"        ❌ Eşik altında (%{SIMILARITY_THRESHOLD*100:.0f})")
        
        # En iyi top_k'yı seç
        ctxs = sorted(ctxs, key=lambda x: x["score"], reverse=True)[:top_k]
        
        print(f"   ✅ {len(ctxs)} kaynak kullanılacak (TOP_K={top_k})")
        
        if ctxs and show_scores:
            print(f"\n   📋 Seçilen Kaynaklar:")
            for i, ctx in enumerate(ctxs, 1):
                preview = ctx['text'][:100].replace('\n', ' ')
                print(f"      {i}. [{ctx['score']:.2%}] {ctx['source']} #{ctx['chunk']}")
                print(f"         → {preview}...")
        
        return ctxs
    
    except Exception as e:
        print(f"❌ Retrieval hatası: {e}")
        import traceback
        traceback.print_exc()
        return []

def ask(question, history):
    """Ana RAG fonksiyonu - akışlı yanıt"""
    if not question.strip():
        yield "⚠️ Lütfen bir soru yazın."
        return
    
    # Retrieval
    ctxs = retrieve(question, show_scores=True)
    
    if not ctxs:
        yield f"""⚠️ **Sorunuzla ilgili bilgi bulunamadı.**

Olası nedenler:
• PDF henüz indekslenmemiş olabilir
• Sorunuz dokümandaki içerikle eşleşmiyor
• Benzerlik eşiği çok yüksek (şu an: {SIMILARITY_THRESHOLD:.0%})

💡 **Öneriler:**
• Soruyu farklı kelimelerle tekrar deneyin
• PDF'nin doğru yüklendiğinden emin olun
• Daha genel sorular sorun"""
        return
    
    # Context'i formatla
    ctx_parts = []
    for i, ctx in enumerate(ctxs, 1):
        ctx_parts.append(
            f"[KAYNAK {i}: {ctx['source']} | Parça #{ctx['chunk']} | "
            f"İlgililik: {ctx['score']:.1%}]\n\n{ctx['text']}"
        )
    ctx_text = "\n\n{'='*60}\n\n".join(ctx_parts)
    
    # Basit ve net prompt
    user_prompt = f"""Aşağıdaki BAĞLAM bilgilerini kullanarak soruyu cevapla.

BAĞLAM:
{ctx_text}

SORU: {question}

CEVAP (Türkçe, bağlama göre):"""

    msgs = [
        {"role": "system", "content": SYSTEM_RAG},
        {"role": "user", "content": user_prompt}
    ]

    try:
        # 🔥 YENİ: Tekrar önleme parametreleri
        resp = client.chat.completions.create(
            model="local",
            messages=msgs,
            temperature=0.3,
            max_tokens=MAX_ANSWER_TOKENS,
            top_p=0.9,
            frequency_penalty=0.6,
            presence_penalty=0.6,
            stop=["BAĞLAM:", "SORU:", "---"],  # 🔥 Döngü kırıcılar
            stream=True,
        )
        
        partial = ""
        
        for chunk in resp:
            delta = chunk.choices[0].delta.content or ""
            partial += delta
            
            yield partial
            
        # Yanıt tamamlanınca kaydet
        log_to_csv(question, partial)
            
    except Exception as e:
        yield f"❌ LLM hatası: {str(e)}"

def ask_with_debug(question, history):
    """Debug modlu soru sorma - kaynak bilgilerini göster"""
    if not question.strip():
        yield "⚠️ Lütfen bir soru yazın."
        return
    
    ctxs = retrieve(question, show_scores=False)
    
    if not ctxs:
        yield "⚠️ İlgili kaynak bulunamadı!"
        return
    
    # Debug bilgisi
    debug_info = "### 🔍 Bulunan Kaynaklar:\n\n"
    for i, ctx in enumerate(ctxs, 1):
        debug_info += f"**{i}. {ctx['source']}** (Parça #{ctx['chunk']})\n"
        debug_info += f"   • İlgililik Skoru: **{ctx['score']:.1%}**\n"
        debug_info += f"   • Uzunluk: {ctx['length']} karakter\n"
        debug_info += f"   • Önizleme: _{ctx['text'][:120].strip()}..._\n\n"
    
    debug_info += "\n---\n\n### 💬 Model Cevabı:\n\n"
    yield debug_info
    
    # Normal yanıt akışı
    ctx_text = "\n\n---\n\n".join([c["text"] for c in ctxs])
    
    user_prompt = f"""BAĞLAM:\n{ctx_text}\n\nSORU: {question}\n\nCEVAP (Türkçe, sadece bağlama göre):"""
    
    msgs = [
        {"role": "system", "content": SYSTEM_RAG},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        resp = client.chat.completions.create(
            model="local",
            messages=msgs,
            temperature=0.3,
            max_tokens=MAX_ANSWER_TOKENS,
            frequency_penalty=0.6,
            presence_penalty=0.6,
            stop=["BAĞLAM:", "---"],
            stream=True,
        )
        
        full_answer = ""
        for chunk in resp:
            delta = chunk.choices[0].delta.content or ""
            debug_info += delta
            full_answer += delta
            
            yield debug_info
            
        # Yanıt tamamlanınca kaydet
        log_to_csv(question, full_answer)
            
    except Exception as e:
        yield debug_info + f"\n\n❌ Hata: {str(e)}"

def summarize_doc():
    """Belgeyi genel olarak özetle"""
    try:
        res = col.get(include=["documents", "metadatas"])
        docs = res.get("documents") or []
        
        if not docs:
            return "⚠️ Özetlenecek belge bulunamadı. Önce bir PDF indeksleyin."
        
        # Tüm chunk'ları birleştir
        all_text = " ".join(docs) if isinstance(docs, list) else str(docs)
        
        # Çok uzunsa ilk N chunk'ı al (limitli context)
        if len(all_text) > 15000:
            sample_chunks = docs[:10] if isinstance(docs, list) else [all_text[:15000]]
            sample_text = " ".join(sample_chunks) if isinstance(sample_chunks, list) else sample_chunks
        else:
            sample_text = all_text
        
        msgs = [
            {"role": "system", "content": "Sen bir uzman doküman analistisin. Verilen metnin genel ve kapsamlı bir özetini çıkar."},
            {"role": "user", "content": f"""Aşağıdaki belgenin içeriğini, ana konusunu ve önemli noktalarını kapsayan genel bir özet yaz.
Anlaşılır paragraflar halinde, akıcı bir Türkçe kullan.

BELGENİN METNİ (Kısmi):
{sample_text}

GENEL ÖZET:"""}
        ]
        
        r = client.chat.completions.create(
            model="local", 
            messages=msgs, 
            temperature=0.3, 
            max_tokens=MAX_ANSWER_TOKENS,
            frequency_penalty=0.5,
            stream=False
        )
        
        summary = r.choices[0].message.content or "Özet oluşturulamadı."
        
        return f"### 📝 Belge Özeti\n\n{summary}\n\n---\n_Not: Bu özet belgenin ilk {len(sample_text)} karakterine dayanmaktadır._"
    
    except Exception as e:
        return f"❌ Özet hatası: {str(e)}"

# ---- GRADIO ARAYÜZÜ ----
with gr.Blocks(title="DOĞAL DİL TABANLI DOKÜMAN ANALİZ SİSTEMİ") as demo:
    gr.Markdown("""
    # 🎯 DOĞAL DİL TABANLI DOKÜMAN ANALİZ SİSTEMİ
    
    ### Özellikler:
    - 📄 PDF metin çıkarma + OCR desteği
    - 🧠 Akıllı vektör tabanlı arama
    - 💬 Bağlama dayalı soru-cevap
    - 🔍 Debug modu ile kaynak görüntüleme
    
    **Model:** BAAI/bge-small-en-v1.5 | **Chunk:** 800 karakter | **Overlap:** 200
    """)

    with gr.Row():
        f = gr.File(label="📁 PDF Dosyası Yükle (.pdf)", file_types=[".pdf"])
    
    with gr.Row():
        idx_btn = gr.Button("📥 PDF'yi İndeksle", variant="primary", size="lg")
        clr_btn = gr.Button("🗑️ Son PDF'i Sil", variant="secondary")
        clr_all_btn = gr.Button("🧹 Tüm İndeksi Sil", variant="stop")
    
    log = gr.Textbox(label="📊 Durum / İstatistikler", interactive=False, lines=8)

    idx_btn.click(fn=index_pdf, inputs=f, outputs=log)
    clr_btn.click(fn=clear_index, inputs=None, outputs=log)
    clr_all_btn.click(fn=clear_all_index, inputs=None, outputs=log)

    gr.Markdown("---")
    gr.Markdown("## 💬 Soru-Cevap")
    
    with gr.Tab("Normal Mod"):
        chat_normal = gr.ChatInterface(
            fn=ask,
            textbox=gr.Textbox(
                placeholder="Örn: Bu belgede deyimler nasıl tanımlanıyor?", 
                container=False,
                scale=7
            )
        )
    
    with gr.Tab("🔍 Debug Mod (Kaynaklarla)"):
        chat_debug = gr.ChatInterface(
            fn=ask_with_debug,
            textbox=gr.Textbox(
                placeholder="Debug modunda kaynak bilgileri de gösterilir", 
                container=False
            )
        )

    gr.Markdown("---")
    gr.Markdown("## 📝 Belge Özeti")
    
    with gr.Row():
        sum_btn = gr.Button("📝 Genel Özet Oluştur", variant="primary")
    
    summary_out = gr.Textbox(label="Özet Sonucu", lines=10)
    sum_btn.click(fn=summarize_doc, inputs=None, outputs=summary_out)
    
    gr.Markdown("""
    ---
    ### 💡 Kullanım İpuçları:
    - Sorularınızı net ve spesifik sorun ("Bu belgede X nedir?")
    - Debug modunu kullanarak hangi kaynakların bulunduğunu görebilirsiniz
    - Benzerlik eşiği: %65 (koddan değiştirilebilir)
    - PDF'yi indekslemeden önce soru sormayın
    """)

server_name = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
demo.launch(server_name=server_name, server_port=7861, share=False)