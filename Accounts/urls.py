from django.urls import path

from .import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('main/', views.main, name='main'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('give_review/', views.give_review, name='give_review'),
    path('remove_user/<str:pk>/', views.removeUser, name="remove_user"),
    path('remove_review/<str:pk>/', views.removeReview, name="remove_review"),
    path('staff_profile/', views.staff_profile, name='staff_profile'),
]
