from django.urls import path
from .import views
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('main/', views.main, name='dashboard'),
    path('login/', views.login, name='login'),
    path('register/', views.registerPage, name='register'),
]
