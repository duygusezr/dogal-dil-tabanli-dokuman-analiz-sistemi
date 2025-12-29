# Türkçe karakter desteği
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Green
Write-Host "Türkçe LLM Sunucusu Başlatılıyor..." -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "Model: Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf"
Write-Host "Port: 8080"
Write-Host "GPU Katmanları: 999 (Tümü)"
Write-Host "Context: 8192 tokens"
Write-Host "Thread: 12"
Write-Host ""
Write-Host "Sunucu başlatılıyor, lütfen bekleyin..."
Write-Host ""

# Dosya yollarını tanımla
$llamaServer = "C:\testLlama\llama.cpp\build\bin\Release\llama-server.exe"
$modelPath = "C:\models\turkish\Turkish-Llama-8b-Instruct-v0.1.Q4_K_S.gguf"

# Komutu çalıştır
& $llamaServer `
  --port 8080 `
  -m $modelPath `
  -c 8192 `
  -ngl 999 `
  -t 12

# Hata durumunda pencerenin kapanmasını engelle
Read-Host "Kapatmak için Enter'a basın..."
