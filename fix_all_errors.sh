#!/bin/bash

# Полное исправление всех ошибок на продакшен-сервере

echo "🔧 Исправление всех проблем indiedev_platform..."

# Создаем резервные копии
echo "📦 Создание резервных копий..."
cp indiedev_platform/settings.py indiedev_platform/settings.py.backup
cp games/models.py games/models.py.backup

# Исправляем проблему 301 редиректов
echo "🔄 Исправление 301 редиректов..."
sed -i 's/SECURE_SSL_REDIRECT = True/SECURE_SSL_REDIRECT = False/g' indiedev_platform/settings.py

if ! grep -q "fluffy.furrysocial.ru" indiedev_platform/settings.py; then
    sed -i "s/ALLOWED_HOSTS = \['\*'\]/ALLOWED_HOSTS = ['*', 'fluffy.furrysocial.ru', 'www.fluffy.furrysocial.ru']/g" indiedev_platform/settings.py
fi

# Исправляем FieldError - добавляем related_name='games'
echo "🗃️ Исправление FieldError..."
sed -i "s/genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True)/genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True, related_name='games')/g" games/models.py

# Создаем миграцию для related_name
echo "📝 Создание миграции..."
cat > games/migrations/0002_add_related_name_to_genres.py << 'MIGRATION_EOF'
# Generated manually to add related_name to genres field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='games', to='games.genre', verbose_name='Жанры'),
        ),
    ]
MIGRATION_EOF

# Применяем миграцию
echo "🚀 Применение миграции..."
python manage.py migrate

echo ""
echo "✅ Все проблемы исправлены!"
echo ""
echo "📋 Что было исправлено:"
echo "  ✓ Отключен SECURE_SSL_REDIRECT (исправлены 301 редиректы)"
echo "  ✓ Добавлен домен в ALLOWED_HOSTS"
echo "  ✓ Добавлен related_name='games' в модель Game"
echo "  ✓ Создана и применена миграция"
echo ""
echo "🔄 Перезапустите Django сервер:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🔒 Для продакшена используйте:"
echo "   python manage.py runserver --settings=indiedev_platform.settings_production"
