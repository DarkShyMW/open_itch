"""
Настройки Django для продакшен-сервера
"""

from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Добавьте ваш домен
ALLOWED_HOSTS = [
    'fluffy.furrysocial.ru',
    'www.fluffy.furrysocial.ru',
    '127.0.0.1',
    'localhost',
]

# Доверенные прокси (для nginx/apache)
USE_TZ = True

# Безопасность - ОТКЛЮЧАЕМ принудительный SSL редирект
# Пусть nginx/веб-сервер обрабатывает HTTPS
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Основные настройки безопасности
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS отключаем до правильной настройки SSL
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_SECONDS = 0

# Cookies - разрешаем работу через HTTP для отладки
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CORS для продакшена
CORS_ALLOWED_ORIGINS = [
    "https://fluffy.furrysocial.ru",
    "http://fluffy.furrysocial.ru",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = True  # Временно для отладки

# Статические файлы для продакшена
STATIC_ROOT = '/var/www/indiedev_platform/static/'

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/indiedev_platform.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# База данных - переключите на PostgreSQL для продакшена
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'indiedev_platform',
#         'USER': 'your_db_user',
#         'PASSWORD': 'your_db_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
