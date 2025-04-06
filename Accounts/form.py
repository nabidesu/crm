from django.forms import ModelForm
from .models import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ReviewForm(ModelForm):
    email = forms.EmailField(
        label="Your Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    audio = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'audio/*',
            'style': 'display: none;',
            'id': 'audioFile'
        })
    )

    class Meta:
        model = Reviews
        fields = ['email', 'review', 'responseAlert', 'audio']
        widgets = {
            'review': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'required': False
            }),
            'responseAlert': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['review'].required = False
        self.fields['review'].help_text = "Optional: Type your review or use the audio recorder"

    def clean(self):
        cleaned_data = super().clean()
        review_text = cleaned_data.get('review')
        audio_file = cleaned_data.get('audio')

        # Require either text or audio review
        if not review_text and not audio_file:
            raise forms.ValidationError(
                "Please provide either a text review or record an audio review"
            )

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not Customer.objects.filter(customerEmail=email, activityStatus=1).exists():
            raise forms.ValidationError(
                "This email is not registered or not verified. Please contact reception."
            )
        return email


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'email', 'password1', 'password2']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customerEmail', 'roomType', 'noOfDays']
