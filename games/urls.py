from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    # Основные страницы
    path('', views.GameListView.as_view(), name='list'),
    path('<slug:slug>/', views.GameDetailView.as_view(), name='detail'),
    
    # Управление играми
    path('create/', views.GameCreateView.as_view(), name='create'),
    path('<slug:slug>/edit/', views.GameUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.GameDeleteView.as_view(), name='delete'),
    path('<slug:slug>/publish/', views.publish_game, name='publish'),
    
    # Файлы и медиа
    path('<slug:slug>/add-file/', views.add_game_file, name='add_file'),
    path('<slug:slug>/add-image/', views.add_game_image, name='add_image'),
    path('<slug:slug>/download/', views.download_game, name='download'),
    path('<slug:slug>/download/<int:file_id>/', views.download_game, name='download_file'),
    
    # Пользовательские списки
    path('my-games/', views.my_games, name='my_games'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('library/', views.library_view, name='library'),
    path('<slug:slug>/wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Жанры
    path('genres/', views.genres_list, name='genres_list'),
    path('genre/<slug:slug>/', views.genre_detail, name='genre_detail'),
]
