# Используем официальный Nginx образ
FROM nginx:alpine

# Копируем конфигурацию Nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Копируем статические файлы
COPY public/ /usr/share/nginx/html/

# Открываем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]