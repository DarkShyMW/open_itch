from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Основные API эндпоинты
router = DefaultRouter()

# Можно добавить ViewSets для API
# router.register(r'games', GameViewSet)
# router.register(r'users', UserViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    # Дополнительные API эндпоинты
]
