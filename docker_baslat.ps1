# Docker Başlatma Scripti
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Proje Docker Üzerinde Başlatılıyor..." -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "Lütfen bekleyin, ilk açılışta kurulum biraz sürebilir..." -ForegroundColor Yellow
Write-Host ""

# Docker Compose'u çalıştır
docker-compose up --build

# Kapanırsa beklet
Write-Host ""
Read-Host "Kapatmak için Enter'a basın..."
