from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from PIL import Image
import os


class User(AbstractUser):
    """Расширенная модель пользователя"""
    email = models.EmailField('Электронная почта', unique=True)
    is_developer = models.BooleanField('Является разработчиком', default=False)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('О себе', max_length=500, blank=True)
    date_of_birth = models.DateField('Дата рождения', blank=True, null=True)
    location = models.CharField('Местоположение', max_length=100, blank=True)
    website = models.URLField('Веб-сайт', blank=True)
    
    # Социальные сети
    twitter = models.CharField('Twitter', max_length=100, blank=True)
    github = models.CharField('GitHub', max_length=100, blank=True)
    
    # Настройки конфиденциальности
    email_notifications = models.BooleanField('Уведомления по эл. почте', default=True)
    public_profile = models.BooleanField('Публичный профиль', default=True)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.username
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Сжатие аватара
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def games_count(self):
        if self.is_developer:
            return self.developed_games.count()
        return 0
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.following.count()


class DeveloperProfile(models.Model):
    """Профиль разработчика"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='developer_profile')
    display_name = models.CharField('Отображаемое имя', max_length=100)
    company = models.CharField('Компания', max_length=100, blank=True)
    website = models.URLField('Веб-сайт', blank=True)
    bio = models.TextField('Описание', max_length=1000)
    
    # Верификация
    verified = models.BooleanField('Подтвержден', default=False)
    verification_requested = models.BooleanField('Запрошена верификация', default=False)
    
    # Платежные данные
    stripe_account_id = models.CharField('Stripe Account ID', max_length=100, blank=True)
    payout_enabled = models.BooleanField('Выплаты включены', default=False)
    
    # Статистика
    total_earnings = models.DecimalField('Общие поступления', max_digits=10, decimal_places=2, default=0)
    total_downloads = models.PositiveIntegerField('Общие скачивания', default=0)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Профиль разработчика'
        verbose_name_plural = 'Профили разработчиков'
    
    def __str__(self):
        return f"{self.display_name} ({self.user.username})"
    
    def get_absolute_url(self):
        return reverse('accounts:developer_profile', kwargs={'username': self.user.username})


class Follow(models.Model):
    """Модель подписок"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
    
    def __str__(self):
        return f"{self.follower.username} подписан на {self.following.username}"
