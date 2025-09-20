from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, Http404, HttpResponse, FileResponse
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Game, GameFile, GameImage, Genre, Download, Wishlist
from .forms import GameForm, GameFileForm, GameImageForm, GameSearchForm, GamePublishForm
import os
import mimetypes


class GameListView(ListView):
    """Список всех игр"""
    model = Game
    template_name = 'games/game_list.html'
    context_object_name = 'games'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Game.objects.filter(is_published=True).select_related('developer')
        
        # Поиск
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        # Фильтрация по жанрам
        genres = self.request.GET.getlist('genres')
        if genres:
            queryset = queryset.filter(genres__id__in=genres).distinct()
        
        # Фильтрация по платформам
        if self.request.GET.get('windows'):
            queryset = queryset.filter(windows_support=True)
        if self.request.GET.get('mac'):
            queryset = queryset.filter(mac_support=True)
        if self.request.GET.get('linux'):
            queryset = queryset.filter(linux_support=True)
        if self.request.GET.get('android'):
            queryset = queryset.filter(android_support=True)
        if self.request.GET.get('ios'):
            queryset = queryset.filter(ios_support=True)
        
        # Сортировка
        sort = self.request.GET.get('sort', '-created_at')
        if sort:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = GameSearchForm(self.request.GET)
        context['genres'] = Genre.objects.all()
        context['featured_games'] = Game.objects.filter(featured=True, is_published=True)[:5]
        return context


class GameDetailView(DetailView):
    """Подробное описание игры"""
    model = Game
    template_name = 'games/game_detail.html'
    context_object_name = 'game'
    
    def get_object(self):
        game = get_object_or_404(Game, slug=self.kwargs['slug'])
        
        # Увеличиваем счетчик просмотров
        game.view_count += 1
        game.save(update_fields=['view_count'])
        
        return game
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        
        # Проверяем, купил ли пользователь игру
        context['user_owns_game'] = False
        context['in_wishlist'] = False
        
        if self.request.user.is_authenticated:
            context['user_owns_game'] = game.user_can_download(self.request.user)
            context['in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user, game=game
            ).exists()
        
        # Получаем файлы и скриншоты
        context['game_files'] = game.files.all().order_by('platform')
        context['screenshots'] = game.images.all().order_by('order')
        
        # Получаем отзывы
        from social.models import Review
        context['reviews'] = Review.objects.filter(
            game=game, is_public=True
        ).select_related('user').order_by('-created_at')[:10]
        
        # Похожие игры
        context['similar_games'] = Game.objects.filter(
            genres__in=game.genres.all(),
            is_published=True
        ).exclude(id=game.id).distinct()[:6]
        
        return context


class GameCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание новой игры"""
    model = Game
    form_class = GameForm
    template_name = 'games/game_create.html'
    
    def test_func(self):
        return self.request.user.is_developer
    
    def form_valid(self, form):
        form.instance.developer = self.request.user
        messages.success(self.request, 'Игра успешно создана!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('games:edit', kwargs={'slug': self.object.slug})


class GameUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование игры"""
    model = Game
    form_class = GameForm
    template_name = 'games/game_edit.html'
    
    def test_func(self):
        game = self.get_object()
        return self.request.user == game.developer
    
    def form_valid(self, form):
        messages.success(self.request, 'Игра успешно обновлена!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        context['game_files'] = game.files.all()
        context['screenshots'] = game.images.all()
        return context


class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление игры"""
    model = Game
    template_name = 'games/game_delete.html'
    success_url = reverse_lazy('games:my_games')
    
    def test_func(self):
        game = self.get_object()
        return self.request.user == game.developer
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Игра успешно удалена!')
        return super().delete(request, *args, **kwargs)


@login_required
def my_games(request):
    """Мои игры (для разработчиков)"""
    if not request.user.is_developer:
        messages.error(request, 'У вас нет прав для доступа к этой странице.')
        return redirect('games:list')
    
    games = Game.objects.filter(developer=request.user).order_by('-created_at')
    
    # Статистика
    total_downloads = sum(game.download_count for game in games)
    
    context = {
        'games': games,
        'total_downloads': total_downloads,
        'published_count': games.filter(is_published=True).count(),
        'draft_count': games.filter(is_published=False).count(),
    }
    
    return render(request, 'games/my_games.html', context)


@login_required
def add_game_file(request, slug):
    """Добавление файла игры"""
    game = get_object_or_404(Game, slug=slug, developer=request.user)
    
    if request.method == 'POST':
        form = GameFileForm(request.POST, request.FILES)
        if form.is_valid():
            game_file = form.save(commit=False)
            game_file.game = game
            game_file.save()
            messages.success(request, 'Файл успешно добавлен!')
            return redirect('games:edit', slug=game.slug)
    else:
        form = GameFileForm()
    
    return render(request, 'games/add_file.html', {'form': form, 'game': game})


@login_required
def add_game_image(request, slug):
    """Добавление скриншота игры"""
    game = get_object_or_404(Game, slug=slug, developer=request.user)
    
    if request.method == 'POST':
        form = GameImageForm(request.POST, request.FILES)
        if form.is_valid():
            game_image = form.save(commit=False)
            game_image.game = game
            game_image.save()
            messages.success(request, 'Скриншот успешно добавлен!')
            return redirect('games:edit', slug=game.slug)
    else:
        form = GameImageForm()
    
    return render(request, 'games/add_image.html', {'form': form, 'game': game})


@login_required
def publish_game(request, slug):
    """Публикация игры"""
    game = get_object_or_404(Game, slug=slug, developer=request.user)
    
    # Проверяем, что у игры есть необходимые данные
    errors = []
    if not game.cover_image:
        errors.append('Необходимо добавить обложку')
    if not game.files.exists():
        errors.append('Необходимо добавить хотя бы один файл игры')
    
    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect('games:edit', slug=game.slug)
    
    if request.method == 'POST':
        form = GamePublishForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            if game.is_published:
                messages.success(request, 'Игра успешно опубликована!')
            else:
                messages.info(request, 'Игра снята с публикации')
            return redirect('games:detail', slug=game.slug)
    else:
        form = GamePublishForm(instance=game)
    
    return render(request, 'games/publish_game.html', {'form': form, 'game': game})


def download_game(request, slug, file_id=None):
    """Скачивание игры"""
    game = get_object_or_404(Game, slug=slug, is_published=True)
    
    # Проверяем права на скачивание
    if not game.user_can_download(request.user):
        messages.error(request, 'У вас нет прав на скачивание этой игры.')
        return redirect('games:detail', slug=game.slug)
    
    # Определяем файл для скачивания
    if file_id:
        game_file = get_object_or_404(GameFile, id=file_id, game=game)
    else:
        game_file = game.files.first()
        if not game_file:
            messages.error(request, 'Файлы для скачивания не найдены.')
            return redirect('games:detail', slug=game.slug)
    
    # Записываем статистику скачивания
    Download.objects.create(
        user=request.user if request.user.is_authenticated else None,
        game=game,
        game_file=game_file,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Обновляем счетчики
    game.download_count += 1
    game.save(update_fields=['download_count'])
    
    game_file.download_count += 1
    game_file.save(update_fields=['download_count'])
    
    # Отдаем файл
    try:
        return FileResponse(
            open(game_file.file.path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(game_file.file.name)
        )
    except FileNotFoundError:
        messages.error(request, 'Файл не найден.')
        return redirect('games:detail', slug=game.slug)


@login_required
def toggle_wishlist(request, slug):
    """Добавление/удаление из списка желаний"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    game = get_object_or_404(Game, slug=slug, is_published=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        game=game
    )
    
    if not created:
        wishlist_item.delete()
        in_wishlist = False
        action = 'removed'
    else:
        in_wishlist = True
        action = 'added'
    
    return JsonResponse({
        'in_wishlist': in_wishlist,
        'action': action
    })


@login_required
def wishlist_view(request):
    """Список желаний пользователя"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('game').order_by('-created_at')
    
    return render(request, 'games/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def library_view(request):
    """Библиотека скачанных игр"""
    downloaded_games = Game.objects.filter(
        downloads__user=request.user,
        is_published=True
    ).select_related('developer').distinct().order_by('-downloads__created_at')
    
    return render(request, 'games/library.html', {
        'downloaded_games': downloaded_games
    })


def genres_list(request):
    """Список всех жанров"""
    genres = Genre.objects.annotate(
        games_count=Count('games', filter=Q(games__is_published=True))
    ).order_by('name')
    
    return render(request, 'games/genres_list.html', {'genres': genres})


def genre_detail(request, slug):
    """Игры конкретного жанра"""
    genre = get_object_or_404(Genre, slug=slug)
    games = Game.objects.filter(
        genres=genre, is_published=True
    ).select_related('developer').order_by('-created_at')
    
    paginator = Paginator(games, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'games/genre_detail.html', {
        'genre': genre,
        'games': page_obj,
        'page_obj': page_obj
    })
