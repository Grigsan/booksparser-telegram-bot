@echo off
chcp 65001 > nul
echo ========================================
echo   ЗАПУСК TELEGRAM-БОТА "ГОСПОДИН АЛЛАДИН"
echo ========================================
echo.

echo [1/4] Проверка Docker...
docker --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не установлен или не запущен!
    pause
    exit /b 1
)

echo [2/4] Остановка старых контейнеров...
docker-compose down

echo [3/4] Сборка и запуск бота...
docker-compose up --build -d

echo [4/4] Проверка статуса...
timeout /t 3 /nobreak > nul
docker ps --filter "name=telegram_moderator_bot"

echo.
echo ========================================
echo   БОТ ЗАПУЩЕН!
echo ========================================
echo.
echo 📱 Добавьте бота в Telegram группу
echo 🔧 Назначьте права администратора
echo 📊 Логи: docker logs telegram_moderator_bot
echo 🛑 Остановка: docker-compose down
echo.
echo Веб-интерфейс: http://localhost:8080 (если настроен)
echo.
pause
