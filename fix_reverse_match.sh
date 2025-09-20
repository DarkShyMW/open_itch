#!/bin/bash

echo "🔧 Исправление ошибки NoReverseMatch для жанров..."
echo "=================================================="

# Выполняем скрипт исправления slug
echo "📝 Исправляем пустые slug у жанров..."
python manage.py shell -c "
import os
import django
from django.utils.text import slugify
from games.models import Genre

print('🔍 Поиск жанров с пустыми slug...')
empty_slug_genres = Genre.objects.filter(slug='') | Genre.objects.filter(slug__isnull=True)

if not empty_slug_genres.exists():
    print('✅ Все жанры имеют корректные slug!')
else:
    print(f'📝 Найдено {empty_slug_genres.count()} жанров с пустыми slug:')
    
    for genre in empty_slug_genres:
        old_slug = genre.slug or '[пусто]'
        genre.slug = slugify(genre.name)
        
        try:
            genre.save()
            print(f'   ✅ {genre.name}: {old_slug} → {genre.slug}')
        except Exception as e:
            print(f'   ❌ Ошибка при сохранении {genre.name}: {e}')
    
    print('🚀 Исправление slug завершено!')
"

echo
echo "✅ Исправление завершено!"
echo
echo "📋 Что было исправлено:"
echo "   ✅ Обновлены slug полей у жанров с пустыми значениями"
echo "   ✅ Обновлен шаблон base.html для защиты от пустых slug"
echo
echo "🚀 Перезапустите Django сервер:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo
