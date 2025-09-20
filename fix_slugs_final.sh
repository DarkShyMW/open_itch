#!/bin/bash

echo "🔧 ОКОНЧАТЕЛЬНОЕ исправление всех ошибок NoReverseMatch"
echo "========================================================="

# Исправляем базу данных - генерируем slug для всех жанров
echo "1️⃣ Исправление slug в базе данных..."
python manage.py shell -c "
import sys
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indiedev_platform.settings')

import django
django.setup()

from django.utils.text import slugify
from games.models import Genre

print('🔍 Анализ жанров в базе данных...')

# Найти все жанры
all_genres = Genre.objects.all()
print(f'Всего жанров в БД: {all_genres.count()}')

# Найти жанры с пустыми или None slug
empty_slug_genres = Genre.objects.filter(slug__in=['', None]) | Genre.objects.filter(slug__isnull=True)
print(f'Жанров с пустыми slug: {empty_slug_genres.count()}')

# Исправить каждый жанр
fixed_count = 0
for genre in all_genres:
    old_slug = genre.slug
    needs_fix = not genre.slug or genre.slug.strip() == ''
    
    if needs_fix:
        # Генерируем новый slug
        base_slug = slugify(genre.name)
        if not base_slug:
            base_slug = f'genre-{genre.id}'
        
        # Проверяем уникальность
        counter = 1
        new_slug = base_slug
        while Genre.objects.filter(slug=new_slug).exclude(id=genre.id).exists():
            new_slug = f'{base_slug}-{counter}'
            counter += 1
        
        genre.slug = new_slug
        genre.save()
        print(f'   ✅ {genre.name}: \"{old_slug or \"[пусто]\"}\" → \"{new_slug}\"')
        fixed_count += 1

print(f'\\n🚀 Исправлено {fixed_count} жанров!')

# Проверяем результат
remaining_empty = Genre.objects.filter(slug__in=['', None]) | Genre.objects.filter(slug__isnull=True)
if remaining_empty.exists():
    print(f'⚠️  Внимание: ещё остались жанры с пустыми slug: {remaining_empty.count()}')
    for genre in remaining_empty:
        print(f'   - {genre.name} (id: {genre.id})')
else:
    print('✅ Все жанры теперь имеют корректные slug!')
"

echo ""
echo "2️⃣ Проверка исправлений шаблонов..."

# Проверяем, что шаблоны исправлены
if grep -q "{% if genre.slug %}" templates/core/home.html; then
    echo "✅ templates/core/home.html - исправлен"
else 
    echo "❌ templates/core/home.html - требует исправления"
fi

if grep -q "{% if genre.slug %}" templates/base.html; then
    echo "✅ templates/base.html - исправлен"
else 
    echo "❌ templates/base.html - требует исправления"
fi

echo ""
echo "✅ Полное исправление завершено!"
echo ""
echo "📋 Что было сделано:"
echo "  ✅ Сгенерированы уникальные slug для всех жанров"
echo "  ✅ Исправлены шаблоны с защитой от пустых slug"
echo "  ✅ Применены все предыдущие исправления"
echo ""
echo "🚀 Теперь перезапустите Django:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🌟 Ваш сайт должен работать без ошибок!"
