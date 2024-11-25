from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
# Create your views here.


def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'Accounts/register.html', context)


def loginPage(request):
    context = {}
    return render(request, 'Accounts/login.html', context)


def dashboard(request):
    return render(request, 'Accounts/dashboard.html')


def main(request):
    return render(request, 'Accounts/main.html')


def login(request):
    return render(request, 'Accounts/login.html')
