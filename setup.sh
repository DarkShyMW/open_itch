#!/bin/bash

# Скрипт для первого запуска проекта

echo "🚀 Настройка бесплатной платформы для инди-разработчиков..."

# Переход в папку проекта
cd indiedev_platform

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install -r requirements.txt

# Создание миграций
echo "📄 Создание миграций..."
python manage.py makemigrations accounts
python manage.py makemigrations games
python manage.py makemigrations social
python manage.py makemigrations

# Применение миграций
echo "🔄 Применение миграций..."
python manage.py migrate

# Создание суперпользователя
echo "👤 Создание суперпользователя..."
echo "Введите данные для администратора:"
python manage.py createsuperuser

# Создание начальных данных
echo "🌱 Создание начальных данных..."
python manage.py shell << EOF
from games.models import Genre

# Создаем основные жанры
genres_data = [
    {'name': 'Акшен', 'color': '#ff6b35'},
    {'name': 'Приключения', 'color': '#17a2b8'},
    {'name': 'RPG', 'color': '#8e44ad'},
    {'name': 'Стратегия', 'color': '#2ecc71'},
    {'name': 'Платформер', 'color': '#e67e22'},
    {'name': 'Головоломка', 'color': '#f39c12'},
    {'name': 'Аркада', 'color': '#e74c3c'},
    {'name': 'Инди', 'color': '#9b59b6'},
    {'name': 'Симулятор', 'color': '#34495e'},
    {'name': 'Роголайк', 'color': '#c0392b'},
]

for genre_data in genres_data:
    Genre.objects.get_or_create(
        name=genre_data['name'],
        defaults={'color': genre_data['color']}
    )

print("Жанры созданы!")
EOF

# Создание папок для медиа
echo "📁 Создание папок для медиа..."
mkdir -p media/avatars
mkdir -p media/games/covers
mkdir -p media/games/banners
mkdir -p media/games/screenshots
mkdir -p media/games/files
mkdir -p media/posts

echo "✅ Настройка завершена!"
echo "🎉 Платформа готова к запуску!"
echo ""
echo "🚀 Для запуска сервера выполните:"
echo "   python manage.py runserver"
echo ""
echo "🌐 Платформа будет доступна по адресу: http://127.0.0.1:8000/"
echo "🔐 Админ-панель: http://127.0.0.1:8000/admin/"
