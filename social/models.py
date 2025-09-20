from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from games.models import Game


class Review(models.Model):
    """Отзывы на игры"""
    
    RATING_CHOICES = [
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Отзыв')
    rating = models.IntegerField(
        'Оценка', 
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    recommended = models.BooleanField('Рекомендую', default=True)
    is_public = models.BooleanField('Публичный', default=True)
    
    # Полезность отзыва
    helpful_count = models.PositiveIntegerField('Полезно', default=0)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    # Комментарии и лайки
    comments = GenericRelation('Comment')
    likes = GenericRelation('Like')
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('user', 'game')  # Один отзыв на игру
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.rating}/5)"
    
    def get_absolute_url(self):
        return reverse('social:review_detail', kwargs={'pk': self.pk})
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.filter(is_public=True).count()


class GameRating(models.Model):
    """Простая оценка игры (без отзыва)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_ratings')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    created_at = models.DateTimeField('Дата оценки', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Оценка игры'
        verbose_name_plural = 'Оценки игр'
        unique_together = ('user', 'game')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.game.title} ({self.rating}/5)"


class Comment(models.Model):
    """Комментарии (универсальные)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField('Комментарий')
    
    # Generic Foreign Key для комментирования любых объектов
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Иерархия комментариев
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    is_public = models.BooleanField('Публичный', default=True)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    # Лайки комментариев
    likes = GenericRelation('Like')
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}..."
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def replies_count(self):
        return self.replies.filter(is_public=True).count()


class Like(models.Model):
    """Лайки (универсальные)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    
    # Generic Foreign Key для лайков любых объектов
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField('Дата лайка', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} liked {self.content_object}"


class Post(models.Model):
    """Посты разработчиков"""
    
    TYPE_CHOICES = [
        ('news', 'Новости'),
        ('dev_log', 'Дневник разработки'),
        ('release', 'Релиз'),
        ('update', 'Обновление'),
        ('general', 'Общее'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Слаг', unique=True, max_length=200)
    content = models.TextField('Контент')
    excerpt = models.CharField('Краткое описание', max_length=300, blank=True)
    
    post_type = models.CharField('Тип поста', max_length=20, choices=TYPE_CHOICES, default='general')
    
    # Медиа
    featured_image = models.ImageField('Изображение', upload_to='posts/', blank=True, null=True)
    
    # Публикация
    is_published = models.BooleanField('Опубликовано', default=True)
    is_pinned = models.BooleanField('Закреплено', default=False)
    
    # Статистика
    view_count = models.PositiveIntegerField('Количество просмотров', default=0)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    published_at = models.DateTimeField('Опубликовано', null=True, blank=True)
    
    # Комментарии и лайки
    comments = GenericRelation('Comment')
    likes = GenericRelation('Like')
    
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('social:post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.filter(is_public=True).count()


class Notification(models.Model):
    """Уведомления"""
    
    TYPE_CHOICES = [
        ('like', 'Лайк'),
        ('comment', 'Комментарий'),
        ('follow', 'Подписка'),
        ('review', 'Отзыв'),
        ('purchase', 'Покупка'),
        ('game_update', 'Обновление игры'),
        ('system', 'Системное'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    
    notification_type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES)
    title = models.CharField('Заголовок', max_length=200)
    message = models.TextField('Сообщение')
    
    # Ссылка на связанный объект
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Ссылка для перехода
    action_url = models.URLField('Ссылка', blank=True)
    
    is_read = models.BooleanField('Прочитано', default=False)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])


class ReportContent(models.Model):
    """Жалобы на контент"""
    
    REASON_CHOICES = [
        ('spam', 'Спам'),
        ('harassment', 'Харасмент'),
        ('hate_speech', 'Язык ненависти'),
        ('inappropriate', 'Неподходящий контент'),
        ('copyright', 'Нарушение авторских прав'),
        ('other', 'Другое'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('reviewed', 'Рассмотрена'),
        ('resolved', 'Решена'),
        ('dismissed', 'Отклонена'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    
    # Объект жалобы
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    reason = models.CharField('Причина', max_length=20, choices=REASON_CHOICES)
    description = models.TextField('Описание', blank=True)
    
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Модерация
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reports')
    moderator_note = models.TextField('Примечание модератора', blank=True)
    
    created_at = models.DateTimeField('Дата жалобы', auto_now_add=True)
    resolved_at = models.DateTimeField('Дата решения', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Жалоба от {self.reporter.username} - {self.get_reason_display()}"
