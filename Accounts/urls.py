from django.urls import path, include

from .import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.root_redirect, name='root_redirect'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('main/', views.main, name='main'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('give_review/', views.give_review, name='give_review'),
    path('remove_user/<str:pk>/', views.removeUser, name="remove_user"),
    path('remove_review/<str:pk>/', views.removeReview, name="remove_review"),
    path('remove_customer/<str:pk>/',
         views.removeCustomer, name='remove_customer'),
    path('staff_profile/', views.staff_profile, name='staff_profile'),
    path('verify_customer/<str:verification_token>/',
         views.verify_customer, name='verify_customer'),
    path('customer_registration/', views.register_customer,
         name='register_customer'),
    path('confirmation/', views.confirmation_page, name='confirmation'),
    path('customer_info/', views.customer_info, name='customer_info'),

]
