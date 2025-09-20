from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import User, DeveloperProfile, Follow
from .forms import CustomUserCreationForm, UserProfileForm, DeveloperProfileForm, LoginForm


def register_view(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать! Вы успешно зарегистрировались.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Устанавливаем время жизни сессии
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Сессия до закрытия браузера
            
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('home')


class ProfileView(DetailView):
    """Просмотр профиля пользователя"""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Проверяем, подписан ли текущий пользователь
        context['is_following'] = False
        if self.request.user.is_authenticated and self.request.user != user:
            context['is_following'] = Follow.objects.filter(
                follower=self.request.user, following=user
            ).exists()
        
        # Получаем игры пользователя
        if user.is_developer:
            context['user_games'] = user.developed_games.filter(is_published=True)[:6]
        
        # Получаем последние отзывы
        context['recent_reviews'] = user.reviews.filter(is_public=True).order_by('-created_at')[:5]
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile_edit')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)


class DeveloperProfileView(DetailView):
    """Просмотр профиля разработчика"""
    model = User
    template_name = 'accounts/developer_profile.html'
    context_object_name = 'developer'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        if not user.is_developer:
            return redirect('accounts:profile', username=user.username)
        
        context['developer_profile'] = get_object_or_404(DeveloperProfile, user=user)
        context['games'] = user.developed_games.filter(is_published=True)
        context['total_downloads'] = sum(game.download_count for game in context['games'])
        
        return context


@login_required
def developer_profile_edit(request):
    """Редактирование профиля разработчика"""
    if not request.user.is_developer:
        messages.error(request, 'У вас нет прав для редактирования профиля разработчика.')
        return redirect('accounts:profile', username=request.user.username)
    
    try:
        developer_profile = request.user.developer_profile
    except DeveloperProfile.DoesNotExist:
        developer_profile = DeveloperProfile.objects.create(
            user=request.user,
            display_name=request.user.username,
            bio=''
        )
    
    if request.method == 'POST':
        form = DeveloperProfileForm(request.POST, instance=developer_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль разработчика обновлен!')
            return redirect('accounts:developer_profile_edit')
    else:
        form = DeveloperProfileForm(instance=developer_profile)
    
    return render(request, 'accounts/edit_developer_profile.html', {'form': form})


@login_required
def toggle_follow(request, username):
    """Переключение подписки на пользователя"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    target_user = get_object_or_404(User, username=username)
    
    if request.user == target_user:
        return JsonResponse({'error': 'Нельзя подписаться на себя'}, status=400)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )
    
    if not created:
        follow.delete()
        is_following = False
        action = 'unfollowed'
    else:
        is_following = True
        action = 'followed'
    
    return JsonResponse({
        'is_following': is_following,
        'action': action,
        'followers_count': target_user.followers_count
    })


def search_users(request):
    """Поиск пользователей"""
    query = request.GET.get('q', '')
    users = []
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).filter(public_profile=True)[:10]
    
    return render(request, 'accounts/search_users.html', {
        'users': users,
        'query': query
    })


def developers_list(request):
    """Список разработчиков"""
    developers = User.objects.filter(
        is_developer=True,
        public_profile=True
    ).select_related('developer_profile').order_by('-developer_profile__total_downloads')
    
    # Фильтрация
    verified_only = request.GET.get('verified') == 'true'
    if verified_only:
        developers = developers.filter(developer_profile__verified=True)
    
    query = request.GET.get('q')
    if query:
        developers = developers.filter(
            Q(username__icontains=query) |
            Q(developer_profile__display_name__icontains=query) |
            Q(developer_profile__company__icontains=query)
        )
    
    return render(request, 'accounts/developers_list.html', {
        'developers': developers,
        'query': query,
        'verified_only': verified_only
    })
