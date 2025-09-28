@echo off
echo ========================================
echo   ВОССТАНОВЛЕНИЕ ПРОЕКТА TEHNOPARSER
echo ========================================
echo.

echo [1/4] Остановка контейнеров...
docker-compose down

echo [2/4] Восстановление файлов проекта...
xcopy /E /I /Y project_files\* ..\

echo [3/4] Запуск контейнеров...
cd ..
docker-compose up -d --build

echo [4/4] Проверка статуса...
timeout /t 5 /nobreak > nul
docker ps

echo.
echo ========================================
echo   ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО!
echo ========================================
echo.
echo Веб-интерфейс: http://localhost:80
echo API: http://localhost:5000
echo.
echo Для восстановления базы данных PostgreSQL
echo используйте файл: postgresql_backup.json
echo.
pause
