#!/bin/bash

# Быстрое исправление ошибки 301 на сервере

echo "🔧 Исправление ошибки 301 редиректов..."

# Найти и заменить проблемную строку в settings.py
sed -i 's/SECURE_SSL_REDIRECT = True/SECURE_SSL_REDIRECT = False/g' indiedev_platform/settings.py

# Добавить домен в ALLOWED_HOSTS, если его нет
if ! grep -q "fluffy.furrysocial.ru" indiedev_platform/settings.py; then
    sed -i "s/ALLOWED_HOSTS = \['\*'\]/ALLOWED_HOSTS = ['*', 'fluffy.furrysocial.ru', 'www.fluffy.furrysocial.ru']/g" indiedev_platform/settings.py
fi

echo "✅ Настройки исправлены!"
echo "🔄 Перезапустите Django сервер:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "📝 Или используйте продакшен настройки:"
echo "   python manage.py runserver --settings=indiedev_platform.settings_production"
