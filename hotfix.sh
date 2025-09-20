#!/usr/bin/env python3
"""
Скрипт для исправления пустых slug полей у жанров
"""
import os
import sys
import django
# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indiedev_platform.settings')
django.setup()
from django.utils.text import slugify
from games.models import Genre
def fix_genre_slugs():
    """Исправляет пустые или некорректные slug у жанров"""
    print("🔍 Поиск жанров с пустыми slug...")
    
    # Найдем все жанры с пустыми slug
    empty_slug_genres = Genre.objects.filter(slug='') | Genre.objects.filter(slug__isnull=True)
    
    if not empty_slug_genres.exists():
        print("✅ Все жанры имеют корректные slug!")
        return
    
    print(f"📝 Найдено {empty_slug_genres.count()} жанров с пустыми slug:")
    
    for genre in empty_slug_genres:
        old_slug = genre.slug
        genre.slug = slugify(genre.name)
        
        try:
            genre.save()
            print(f"   ✅ {genre.name}: '{old_slug}' → '{genre.slug}'")
        except Exception as e:
            print(f"   ❌ Ошибка при сохранении {genre.name}: {e}")
    
    print("\n🚀 Исправление завершено!")
if __name__ == '__main__':
    fix_genre_slugs()