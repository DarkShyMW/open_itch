# 🚀 Деплой на продакшен-сервер

## 🔧 Решение проблем

### ❌ Проблема 1: 301 редиректы
Вызвана настройкой `SECURE_SSL_REDIRECT = True` в Django.

### ❌ Проблема 2: FieldError 'games'
Отсутствует `related_name='games'` в модели Game.

## 📋 Шаги исправления на сервере:

### 1. Быстрое исправление

Выполните на вашем сервере:

```bash
# Перейдите в директорию проекта
cd /path/to/your/indiedev_platform

# Сделайте резервную копию (рекомендуется)
cp indiedev_platform/settings.py indiedev_platform/settings.py.backup

# Исправьте настройки Django
sed -i 's/SECURE_SSL_REDIRECT = True/SECURE_SSL_REDIRECT = False/g' indiedev_platform/settings.py

# Обновите модель Game (добавьте related_name='games')
# В файле games/models.py строка 46 должна стать:
# genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True, related_name='games')
```

### 2. Применение миграции

```bash
# Создайте файл миграции
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

# Применить миграцию
python manage.py migrate
```

### 3. Обновите модель вручную

В файле `games/models.py` найдите строку 46:

```python
# Было:
genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True)

# Должно стать:
genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True, related_name='games')
```

### 4. Перезапустите сервер

```bash
# Перезапустите Django
python manage.py runserver 0.0.0.0:8000
```

## 📊 Проверка исправлений

После выполнения всех шагов:

1. ✅ Сайт должен открываться без ошибок 301
2. ✅ Главная страница должна загружаться без FieldError
3. ✅ Жанры должны отображаться корректно

## 🔒 Для продакшена

После исправления ошибок настройте правильно:

1. Используйте продакшен-настройки:
```bash
python manage.py runserver --settings=indiedev_platform.settings_production
```

2. Настройте Nginx (см. `nginx.conf`)
3. Используйте Gunicorn вместо `runserver`
4. Настройте SSL сертификат
5. Переключитесь на PostgreSQL

## ⚡ Скрипт автоматического исправления

Создайте и выполните скрипт:

```bash
cat > fix_all_errors.sh << 'EOF'
#!/bin/bash
echo "🔧 Исправление всех ошибок..."

# Исправляем 301 редиректы
sed -i 's/SECURE_SSL_REDIRECT = True/SECURE_SSL_REDIRECT = False/g' indiedev_platform/settings.py

# Исправляем модель Game
sed -i "s/genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True)/genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True, related_name='games')/g" games/models.py

# Создаем миграцию
cat > games/migrations/0002_add_related_name_to_genres.py << 'MIGRATION_EOF'
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('games', '0001_initial')]
    operations = [
        migrations.AlterField(
            model_name='game',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='games', to='games.genre', verbose_name='Жанры'),
        ),
    ]
MIGRATION_EOF

# Применяем миграцию
python manage.py migrate

echo "✅ Все ошибки исправлены!"
echo "🔄 Перезапустите Django сервер"
EOF

chmod +x fix_all_errors.sh
./fix_all_errors.sh
```
