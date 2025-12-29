# Python 3.12 (Sizin sisteminizle aynı sürüm)
FROM python:3.12-slim

# Sistem bağımlılıklarını ve Tesseract-OCR (Türkçe dahil) yükle
RUN apt-get update && apt-get install -y \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-tur \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini oluştur
WORKDIR /app

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY app_rag.py .

# Gradio portunu dışarı aç
EXPOSE 7861

# Uygulamayı başlat
CMD ["python", "app_rag.py"]
