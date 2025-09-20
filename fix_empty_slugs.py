#!/usr/bin/env python3
"""
Простой скрипт для исправления пустых slug у жанров
Запуск: python fix_empty_slugs.py
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indiedev_platform.settings')
django.setup()

from django.utils.text import slugify
from games.models import Genre

def main():
    print("🔧 Исправление пустых slug у жанров...")
    print("=" * 50)
    
    # Получаем все жанры
    all_genres = Genre.objects.all()
    print(f"📊 Всего жанров в базе: {all_genres.count()}")
    
    # Ищем проблемные жанры
    problematic_genres = []
    for genre in all_genres:
        if not genre.slug or genre.slug.strip() == '':
            problematic_genres.append(genre)
    
    if not problematic_genres:
        print("✅ Все жанры уже имеют корректные slug!")
        return
    
    print(f"🔍 Найдено {len(problematic_genres)} жанров с пустыми slug:")
    
    # Исправляем каждый жанр
    for genre in problematic_genres:
        old_slug = genre.slug or "[пусто]"
        
        # Генерируем базовый slug
        base_slug = slugify(genre.name)
        if not base_slug:
            base_slug = f"genre-{genre.id}"
        
        # Проверяем уникальность
        new_slug = base_slug
        counter = 1
        while Genre.objects.filter(slug=new_slug).exclude(id=genre.id).exists():
            new_slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Сохраняем
        genre.slug = new_slug
        genre.save()
        
        print(f"   ✅ {genre.name}: {old_slug} → {new_slug}")
    
    print(f"\n🎉 Успешно исправлено {len(problematic_genres)} жанров!")
    print("\n🚀 Теперь можете перезапустить Django сервер")

if __name__ == "__main__":
    main()
