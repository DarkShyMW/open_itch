from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Отзывы
    # path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    # path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    
    # Посты
    # path('posts/', views.PostListView.as_view(), name='post_list'),
    # path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    
    # Комментарии и лайки
    # path('like/<int:content_type_id>/<int:object_id>/', views.toggle_like, name='toggle_like'),
    # path('comment/<int:content_type_id>/<int:object_id>/', views.add_comment, name='add_comment'),
]
