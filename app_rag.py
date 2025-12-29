# app_rag.py
import os, gradio as gr, fitz
from openai import OpenAI
import pytesseract
from PIL import Image

# ---- Ayarlar ve Yollar ----
# Tesseract OCR Yolu (Docker'da 'tesseract', Windows'ta tam yol)
tess_env = os.getenv("TESSERACT_CMD")
if tess_env:
    pytesseract.pytesseract.tesseract_cmd = tess_env
else:
    # Windows varsayılanı (Fallback)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---- LLM: yerel llama-server (OpenAI uyumlu) ----
# Docker içinden "llm-server", host üzerinden "127.0.0.1"
base_url = os.getenv("LLM_API_URL", "http://127.0.0.1:8080/v1")
client = OpenAI(api_key="local", base_url=base_url)

# ---- Vektör veritabanı & embedding ----
import chromadb
from chromadb.config import Settings
from fastembed import TextEmbedding

# Türkçe için çok dilli model (daha iyi eşleşme):
EMBED_MODEL = "BAAI/bge-small-en-v1.5"   # alternatif: "BAAI/bge-small-en-v1.5" (daha hafif)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 6
MAX_ANSWER_TOKENS = 700
PERSIST_DIR = "./rag_store"
COLLECTION_NAME = "pdf_chunks"

embedder = TextEmbedding(model_name=EMBED_MODEL)

db = chromadb.PersistentClient(path=PERSIST_DIR, settings=Settings(allow_reset=True))
try:
    col = db.get_collection(COLLECTION_NAME)
except:
    col = db.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

def ocr_page(page_pixmap):
    """PyMuPDF pixmap'ini PIL Image'a çevirip OCR yapar."""
    try:
        # Pixmap'ten PIL Image oluştur
        img = Image.frombytes("RGB", [page_pixmap.width, page_pixmap.height], page_pixmap.samples)
        # Türkçe OCR (lang='tur')
        text = pytesseract.image_to_string(img, lang='tur')
        return text
    except Exception as e:
        print(f"OCR Hatası: {e}")
        return ""

def _read_pdf(path):
    doc = fitz.open(path)
    parts = []
    
    print(f"PDF Analiz ediliyor: {path}")
    
    for i, page in enumerate(doc):
        # 1. Yöntem: Doğrudan metin çıkarma
        txt = page.get_text("text")
        
        # Eğer metin çok azsa veya yoksa OCR dene (Fallback)
        if not txt or len(txt.strip()) < 10:
            print(f"Sayfa {i+1} metin içermiyor, OCR deneniyor...")
            try:
                # Sayfayı görüntüye çevir (300 DPI)
                pix = page.get_pixmap(dpi=300)
                ocr_txt = ocr_page(pix)
                if ocr_txt and ocr_txt.strip():
                    txt = ocr_txt
                    print(f"Sayfa {i+1} OCR ile okundu.")
            except Exception as e:
                print(f"Sayfa {i+1} OCR işlemi başarısız: {e}")
        
        if txt and txt.strip():
            parts.append(txt)
            
    return "\n".join(parts)

def _chunkify(text, size, overlap):
    out = []
    i, n = 0, len(text)
    while i < n:
        j = min(i + size, n)
        out.append(text[i:j])
        if j == n: break
        i = max(j - overlap, 0)
    return out

def index_pdf(file):
    if not file:
        return "Önce bir PDF seçin."
    text = _read_pdf(file.name)
    if not text.strip():
        return "PDF’den metin çıkarılamadı."
    chunks = _chunkify(text, CHUNK_SIZE, CHUNK_OVERLAP)
    ids = [f"{os.path.basename(file.name)}::{i}" for i in range(len(chunks))]
    embs = list(embedder.embed(chunks))
    col.add(
        ids=ids,
        documents=chunks,
        embeddings=embs,
        metadatas=[{"source": os.path.basename(file.name), "chunk": i} for i in range(len(chunks))]
    )
    return f"İndeksleme tamam ✅  {os.path.basename(file.name)} → {len(chunks)} parça eklendi."

def clear_index():
    global col
    db.delete_collection(COLLECTION_NAME)
    col = db.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    return "İndeks temizlendi."

SYSTEM_RAG = (
    "Türkçe cevap ver. Sadece verilen bağlamı kullan; bağlamda yoksa 'Bağlamda yok' de. "
    "Kaynaklardan emin olmadığın bilgileri uydurma."
)

def retrieve(question):
    if not question.strip():
        return []
    qv = list(embedder.embed([question]))[0]
    res = col.query(query_embeddings=[qv], n_results=TOP_K, include=["documents","metadatas"])
    ctxs = []
    if res and res.get("documents") and res["documents"][0]:
        for d, m in zip(res["documents"][0], res["metadatas"][0]):
            src = m.get("source","?")
            ch = m.get("chunk","?")
            ctxs.append(f"[Kaynak: {src} | Parça: {ch}]\n{d}")
    return ctxs

def ask(question, history):
    ctxs = retrieve(question)
    ctx_text = "\n\n---\n\n".join(ctxs) if ctxs else "(bağlam bulunamadı)"

    msgs = [
        {"role":"system","content": SYSTEM_RAG},
        {"role":"user","content": f"BAĞLAM:\n{ctx_text}\n\nSORU:\n{question}"}
    ]

    # Akışlı yanıt
    resp = client.chat.completions.create(
        model="local",
        messages=msgs,
        temperature=0.2,
        max_tokens=MAX_ANSWER_TOKENS,
        stream=True,
    )
    partial = ""
    for chunk in resp:
        delta = chunk.choices[0].delta.content or ""
        partial += delta
        yield partial

def summarize_last(n_sentences):
    try:
        # ChromaDB'den tüm dokümanları al
        res = col.get(include=["documents","metadatas"])
        
        # documents yapısını kontrol et ve düzleştir
        docs = res.get("documents") or []
        if not docs:
            return "Özetlenecek bağlam bulunamadı."
        
        # Eğer iç içe liste varsa düzleştir, değilse direkt kullan
        if docs and isinstance(docs[0], list):
            flat = docs[0]
        else:
            flat = docs if isinstance(docs, list) else list(docs)
        
        if not flat:
            return "Özetlenecek bağlam bulunamadı."
        
        # n_sentences'ı integer'a çevir (Slider float döndürebilir)
        n_sent = int(n_sentences)
        
        # İlk TOP_K parçayı al
        sample = "\n\n---\n\n".join(flat[:TOP_K])
        
        msgs = [
            {"role":"system","content":"Türkçe, kısa ve madde madde özet çıkar."},
            {"role":"user","content": f"Aşağıdaki metni {n_sent} maddeyle KISA özetle:\n\n{sample}"}
        ]
        
        r = client.chat.completions.create(
            model="local", 
            messages=msgs, 
            temperature=0.2, 
            max_tokens=MAX_ANSWER_TOKENS,
            stream=False
        )
        
        return r.choices[0].message.content or "Özet oluşturulamadı."
    
    except Exception as e:
        return f"Hata: {str(e)}"

with gr.Blocks(title="Doğal Dil Tabanlı Doküman Analiz Sistemi") as demo:
    gr.Markdown("## Doğal Dil Tabanlı Doküman Analiz Sistemi\nPDF yükle, indeksle ve soru sor. Büyük PDF’lerde context aşımı olmaz.")

    with gr.Row():
        f = gr.File(label="PDF yükle (.pdf)")
    with gr.Row():
        idx_btn = gr.Button("📥 PDF’yi İndeksle")
        clr_btn = gr.Button("🧹 İndeksi Temizle")
    log = gr.Textbox(label="Durum / Log", interactive=False)

    idx_btn.click(fn=index_pdf, inputs=f, outputs=log)
    clr_btn.click(fn=clear_index, inputs=None, outputs=log)

    gr.Markdown("### Soru-Cevap")
    chat = gr.ChatInterface(
        fn=ask,
        textbox=gr.Textbox(placeholder="Örn: Bu belgede önerilen yöntem nedir?", container=False),
        autofocus=True
    )

    with gr.Row():
        n_sent = gr.Slider(3, 10, value=5, step=1, label="Özet madde sayısı")
        sum_btn = gr.Button("📝 Kısa Özet Al")
    summary_out = gr.Textbox(label="Özet", lines=8)
    sum_btn.click(fn=summarize_last, inputs=n_sent, outputs=summary_out)

demo.launch(server_name="127.0.0.1", server_port=7861)
