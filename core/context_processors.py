# Контекстные процессоры
from games.models import Genre
from social.models import Notification


def platform_context(request):
    """Глобальный контекст платформы"""
    context = {
        'platform_name': 'IndieGameHub',
        'platform_tagline': 'Платформа для инди-разработчиков',
        'genres_menu': Genre.objects.all()[:10],
    }
    
    # Уведомления для аутентифицированных пользователей
    if request.user.is_authenticated:
        context['unread_notifications'] = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    
    return context
