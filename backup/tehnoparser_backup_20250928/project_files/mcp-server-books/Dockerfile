FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Копируем файлы
COPY __main__.py .
COPY books_table.db .
COPY books_export.csv .
COPY books_export.json .

# Создаем пользователя
RUN useradd -m -u 1000 booksuser && chown -R booksuser:booksuser /app
USER booksuser

# Экспонируем порт (если нужен HTTP интерфейс)
EXPOSE 8080

# Запускаем MCP сервер
CMD ["python", "__main__.py"]
