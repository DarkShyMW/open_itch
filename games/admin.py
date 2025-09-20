from django.contrib import admin
from .models import Game, GameFile, Genre, GameImage, Download


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'games_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def games_count(self, obj):
        return obj.games.count()
    games_count.short_description = 'Количество игр'


class GameImageInline(admin.TabularInline):
    model = GameImage
    extra = 1
    max_num = 10


class GameFileInline(admin.TabularInline):
    model = GameFile
    extra = 1
    max_num = 5


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'developer', 'is_published', 'download_count', 'created_at')
    list_filter = ('is_published', 'genres', 'created_at')
    search_fields = ('title', 'developer__username', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)
    inlines = [GameImageInline, GameFileInline]
    readonly_fields = ('download_count', 'view_count')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'developer', 'description', 'short_description')
        }),
        ('Медиа', {
            'fields': ('cover_image', 'banner_image')
        }),
        ('Категоризация', {
            'fields': ('genres', 'tags')
        }),
        ('Публикация', {
            'fields': ('is_published', 'featured')
        }),
        ('Статистика', {
            'fields': ('download_count', 'view_count')
        }),
    )

@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'game__title', 'ip_address')
    readonly_fields = ('created_at',)
