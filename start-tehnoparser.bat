@echo off
echo ========================================
echo    Tehnoparser - Парсер книг
echo ========================================
echo.
echo Запуск Docker контейнеров...
docker-compose up -d --build

echo.
echo ========================================
echo Статус контейнеров:
docker ps

echo.
echo ========================================
echo Веб-интерфейс: http://localhost:80
echo API: http://localhost:80/stats
echo ========================================
echo.
pause
