# Docker Başlatma Scripti
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TÜRKÇE LLM + RAG ANALİZ SİSTEMİ      " -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1/2] Eski servisler temizleniyor..." -ForegroundColor Gray
docker-compose down 2>$null

Write-Host "[2/2] Sistem başlatılıyor (Bu işlem dosya boyutuna göre sürebilir)..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Sistem hazır olduğunda şuraya gidin: http://localhost:7861" -ForegroundColor Green
Write-Host ""

# Docker Compose'u çalıştır
docker-compose up --build

# Kapanırsa beklet
Write-Host ""
Write-Host "Sistem kapandı." -ForegroundColor Red
Read-Host "Pencereyi kapatmak için Enter'a basın..."
