from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Q
from games.models import Game, Genre
from accounts.models import User
from social.models import Review, Post


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Рекомендуемые игры
        context['featured_games'] = Game.objects.filter(
            featured=True, is_published=True
        ).select_related('developer')[:6]
        
        # Новые игры
        context['new_games'] = Game.objects.filter(
            is_published=True
        ).select_related('developer').order_by('-created_at')[:8]
        
        # Популярные игры
        context['popular_games'] = Game.objects.filter(
            is_published=True
        ).select_related('developer').order_by('-download_count')[:8]
        
        # Бесплатные игры (все игры теперь бесплатные)
        context['free_games'] = Game.objects.filter(
            is_published=True
        ).select_related('developer').order_by('-created_at')[:6]
        
        # Жанры
        context['genres'] = Genre.objects.annotate(
            games_count=Count('games', filter=Q(games__is_published=True))
        ).filter(games_count__gt=0).order_by('-games_count')[:8]
        
        # Последние отзывы
        context['recent_reviews'] = Review.objects.filter(
            is_public=True
        ).select_related('user', 'game').order_by('-created_at')[:5]
        
        # Последние посты
        context['recent_posts'] = Post.objects.filter(
            is_published=True
        ).select_related('author', 'game').order_by('-created_at')[:4]
        
        # Статистика платформы
        context['stats'] = {
            'total_games': Game.objects.filter(is_published=True).count(),
            'total_developers': User.objects.filter(is_developer=True).count(),
            'total_downloads': sum(game.download_count for game in Game.objects.filter(is_published=True)),
            'total_reviews': Review.objects.filter(is_public=True).count(),
        }
        
        return context


def about_view(request):
    """Страница о платформе"""
    return render(request, 'core/about.html')


def privacy_policy_view(request):
    """Политика конфиденциальности"""
    return render(request, 'core/privacy_policy.html')


def terms_of_service_view(request):
    """Пользовательское соглашение"""
    return render(request, 'core/terms_of_service.html')


def contact_view(request):
    """Страница контактов"""
    return render(request, 'core/contact.html')
