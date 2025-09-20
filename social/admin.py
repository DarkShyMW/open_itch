from django.contrib import admin
from .models import Review, Comment, GameRating, Post, Like


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'rating', 'is_public', 'created_at')
    list_filter = ('rating', 'is_public', 'created_at')
    search_fields = ('user__username', 'game__title', 'title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'game', 'rating', 'title', 'content')
        }),
        ('Настройки', {
            'fields': ('is_public', 'recommended')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_content_object', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('user__username', 'content')
    
    def get_content_object(self, obj):
        return str(obj.content_object)
    get_content_object.short_description = 'Объект'


@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'game__title')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('author__username', 'title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_content_object', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    
    def get_content_object(self, obj):
        return str(obj.content_object)
    get_content_object.short_description = 'Объект'
