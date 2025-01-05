from django.forms import ModelForm
from .models import Reviews
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ReviewForm(ModelForm):
    class Meta:
        model = Reviews
        fields = ['name', 'phone_number', 'review', 'emotion']


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
