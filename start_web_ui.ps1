# Türkçe karakter desteği
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAG Web Arayüzü Başlatılıyor..." -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "Önce LLM sunucusunun çalıştığından emin olun!" -ForegroundColor Yellow
Write-Host "(start_llm_server.ps1 ile başlatın)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Web arayüzü başlatılıyor..."
Write-Host "Tarayıcınızda: http://127.0.0.1:7861"
Write-Host ""

# Scriptin bulunduğu dizine git
Set-Location $PSScriptRoot

# Python uygulamasını çalıştır
python app_rag.py

# Hata durumunda pencerenin kapanmasını engelle
Read-Host "Kapatmak için Enter'a basın..."
