#!/usr/bin/env python
"""
Тест для проверки работоспособности главной страницы
"""

import os
import sys
import django

# Настройка Django
sys.path.append('/workspace/indiedev_platform')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indiedev_platform.settings')

django.setup()

from core.views import HomeView
from django.test import RequestFactory

def test_homepage():
    """Тестирует загрузку главной страницы"""
    try:
        factory = RequestFactory()
        request = factory.get('/')
        
        view = HomeView()
        view.request = request
        
        context = view.get_context_data()
        
        print("✅ Главная страница загружается без ошибок")
        print(f"📊 Найдено жанров: {len(context.get('genres', []))}")
        print(f"🎮 Рекомендуемых игр: {len(context.get('featured_games', []))}")
        print(f"🆕 Новых игр: {len(context.get('new_games', []))}")
        print(f"🔥 Популярных игр: {len(context.get('popular_games', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке главной страницы: {e}")
        return False

if __name__ == "__main__":
    success = test_homepage()
    if success:
        print("\n🎉 Все тесты пройдены успешно!")
        sys.exit(0)
    else:
        print("\n💥 Тесты не прошли!")
        sys.exit(1)
