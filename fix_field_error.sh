#!/bin/bash

# Скрипт для исправления ошибки FieldError на сервере

echo "🔧 Исправление ошибки FieldError..."

# Создаем резервную копию модели
cp games/models.py games/models.py.backup

# Исправляем модель Game - добавляем related_name='games'
sed -i "s/genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True)/genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True, related_name='games')/g" games/models.py

# Создаем файл миграции
cat > games/migrations/0002_add_related_name_to_genres.py << 'EOF'
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
EOF

# Применяем миграцию
python manage.py migrate

echo "✅ FieldError исправлена!"
echo "🔄 Перезапустите Django сервер"
