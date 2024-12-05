# accounts/urls.py
# Django приложение: accounts

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/check-auth/', views.check_auth, name='check_auth'),
    #path('telegram/callback/', views.telegram_callback, name='telegram_callback'),
    #path('test/', views.test, name='test'),
]
