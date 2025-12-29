# Docker Durdurma Scripti
Write-Host "Sistem kapatılıyor..." -ForegroundColor Yellow

# Konteynerleri durdur ve sil
docker-compose down

Write-Host ""
Write-Host "Başarıyla kapatıldı." -ForegroundColor Green
Start-Sleep -Seconds 3
