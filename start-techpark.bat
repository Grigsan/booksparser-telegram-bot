@echo off
echo Запуск парсера Технопарка...
docker-compose up -d
echo Проект запущен!
echo API доступно по адресу: http://localhost:5000
echo Фронтенд доступен по адресу: http://localhost
pause
