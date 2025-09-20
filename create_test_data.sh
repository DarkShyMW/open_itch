#!/bin/bash

# Скрипт для создания тестовых данных в бесплатной платформе

echo "📊 Создание тестовых данных..."

python manage.py shell << 'EOF'
from accounts.models import User
from games.models import Game, Genre

# Создаем тестового разработчика
developer, created = User.objects.get_or_create(
    username='testdev',
    defaults={
        'email': 'dev@example.com',
        'is_developer': True,
        'first_name': 'Иван',
        'last_name': 'Иванов'
    }
)

if created:
    developer.set_password('testpass123')
    developer.save()
    print("Создан разработчик: testdev (пароль: testpass123)")

# Создаем жанры (с проверкой на существование)
try:
    indie_genre, _ = Genre.objects.get_or_create(
        name='Инди',
        defaults={'slug': 'indie', 'color': '#9b59b6'}
    )
except:
    indie_genre = Genre.objects.filter(name='Инди').first()
    if not indie_genre:
        indie_genre = Genre.objects.create(name='Инди', slug='indie', color='#9b59b6')

try:
    action_genre, _ = Genre.objects.get_or_create(
        name='Акшен', 
        defaults={'slug': 'action', 'color': '#e74c3c'}
    )
except:
    action_genre = Genre.objects.filter(name='Акшен').first()
    if not action_genre:
        action_genre = Genre.objects.create(name='Акшен', slug='action', color='#e74c3c')

# Создаем тестовую игру
test_game, created = Game.objects.get_or_create(
    title='Тестовая Инди Игра',
    slug='test-indie-game',
    defaults={
        'developer': developer,
        'description': 'Это тестовая инди-игра для демонстрации возможностей платформы. Полностью бесплатная!',
        'short_description': 'Демонстрационная инди-игра',
        'is_published': True,
        'featured': True,
        'windows_support': True,
        'mac_support': True,
        'linux_support': True,
    }
)

if created:
    test_game.genres.add(indie_genre, action_genre)
    test_game.tags.add('тест', 'демо', 'бесплатно')
    print(f"Создана игра: {test_game.title}")

print("✅ Тестовые данные созданы!")
print("🎮 Разработчик: testdev / testpass123")
print("🎯 Игра: Тестовая Инди Игра")
EOF

echo "🚀 Запустите сервер: python manage.py runserver"
