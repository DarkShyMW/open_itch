from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from accounts.models import User
import os


class Genre(models.Model):
    """Жанры игр"""
    name = models.CharField('Название', max_length=50, unique=True)
    slug = models.SlugField('Слаг', unique=True)
    description = models.TextField('Описание', blank=True)
    color = models.CharField('Цвет', max_length=7, default='#007bff', help_text='HEX цвет')
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Game(models.Model):
    """Модель игры"""
    
    # Основная информация
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', unique=True, max_length=200)
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='developed_games', verbose_name='Разработчик')
    description = models.TextField('Описание')
    short_description = models.CharField('Краткое описание', max_length=300)
    
    # Медиа
    cover_image = models.ImageField('Обложка', upload_to='games/covers/')
    banner_image = models.ImageField('Баннер', upload_to='games/banners/', blank=True, null=True)
    
    # Категоризация
    genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True)
    tags = TaggableManager(verbose_name='Теги', blank=True)
    
    # Публикация
    is_published = models.BooleanField('Опубликовано', default=False)
    featured = models.BooleanField('Рекомендуемое', default=False)
    
    # Системные требования
    windows_support = models.BooleanField('Windows', default=True)
    mac_support = models.BooleanField('macOS', default=False)
    linux_support = models.BooleanField('Linux', default=False)
    android_support = models.BooleanField('Android', default=False)
    ios_support = models.BooleanField('iOS', default=False)
    
    # Статистика
    download_count = models.PositiveIntegerField('Количество скачиваний', default=0)
    view_count = models.PositiveIntegerField('Количество просмотров', default=0)
    
    # Даты
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('games:detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def rating_count(self):
        return self.reviews.count()
    
    @property
    def platforms(self):
        platforms = []
        if self.windows_support:
            platforms.append('Windows')
        if self.mac_support:
            platforms.append('macOS')
        if self.linux_support:
            platforms.append('Linux')
        if self.android_support:
            platforms.append('Android')
        if self.ios_support:
            platforms.append('iOS')
        return platforms
    
    def user_can_download(self, user):
        """Проверяет, может ли пользователь скачать игру (всегда True - все игры бесплатные)"""
        return True


class GameFile(models.Model):
    """Файлы игры"""
    
    PLATFORM_CHOICES = [
        ('windows', 'Windows'),
        ('mac', 'macOS'),
        ('linux', 'Linux'),
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='files')
    name = models.CharField('Название', max_length=200)
    file = models.FileField('Файл', upload_to='games/files/')
    platform = models.CharField('Платформа', max_length=20, choices=PLATFORM_CHOICES)
    version = models.CharField('Версия', max_length=50, default='1.0')
    file_size = models.PositiveIntegerField('Размер файла (байты)', default=0)
    download_count = models.PositiveIntegerField('Количество скачиваний', default=0)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Файл игры'
        verbose_name_plural = 'Файлы игр'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.game.title} - {self.name} ({self.platform})"
    
    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)


class GameImage(models.Model):
    """Изображения игры"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Изображение', upload_to='games/screenshots/')
    caption = models.CharField('Подпись', max_length=200, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Изображение игры'
        verbose_name_plural = 'Изображения игр'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.game.title} - Изображение {self.order}"


class Download(models.Model):
    """Скачивание игры"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads', null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='downloads')
    game_file = models.ForeignKey(GameFile, on_delete=models.CASCADE, related_name='downloads', null=True)
    ip_address = models.GenericIPAddressField('IP адрес')
    user_agent = models.TextField('User Agent', blank=True)
    
    created_at = models.DateTimeField('Дата скачивания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Скачивание'
        verbose_name_plural = 'Скачивания'
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"{user_info} - {self.game.title}"


class Wishlist(models.Model):
    """Список желаний"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='wishlist_entries')
    
    created_at = models.DateTimeField('Добавлено в список', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Позиция списка желаний'
        verbose_name_plural = 'Список желаний'
        unique_together = ('user', 'game')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.game.title}"
