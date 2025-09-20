from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Аутентификация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Профили
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('developer/edit/', views.developer_profile_edit, name='developer_profile_edit'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('developer/<str:username>/', views.DeveloperProfileView.as_view(), name='developer_profile'),
    
    # Подписки
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    
    # Поиск и списки
    path('search/', views.search_users, name='search_users'),
    path('developers/', views.developers_list, name='developers_list'),
]
