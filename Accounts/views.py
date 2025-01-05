from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Reviews
from .form import *
from .filters import ReviewFilter
from .authentication import unauthenticated_user, allowed_users
# from .utils import load_model_and_vectorizer
# from .preprocessing import clean_data
# Create your views here.


@unauthenticated_user
def registerPage(request):

    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='staff')
            user.groups.add(group)
            messages.success(request, "Account created successfully!"+username)
            return redirect('login')
    else:
        print("form errors:", form.errors)
    context = {'form': form}
    return render(request, 'Accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')

        else:
            messages.error(
                request, "Please check your username or password again.")

    # context = {}
    return render(request, 'Accounts/login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def main(request):
    users = User.objects.all()
    return render(request, 'Accounts/main.html', {'users': users})


# @allowed_users(allowed_roles=['admin', 'customer'])
def give_review(request):

    form = ReviewForm()
    if request.method == 'POST':

        form = ReviewForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('dashboard')
        else:
            print(form.errors)

    reviews = Reviews.objects.filter(
        emotion="positive").order_by('-phone_number')[:5]
    context = {'reviews': reviews, 'form': form}
    return render(request, 'Accounts/give_review.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff'])
def dashboard(request):
    reviews = Reviews.objects.all()
    myFilter = ReviewFilter(request.GET, queryset=reviews)
    reviews = myFilter.qs
    context = {'reviews': reviews, 'myFilter': myFilter}
    return render(request, 'Accounts/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def removeUser(request, pk):
    users = User.objects.get(username=pk)
    if request.method == 'POST':
        users.delete()
        return redirect('main')
    context = {'item': users}
    return render(request, 'Accounts/delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff'])
def removeReview(request, pk):
    reviews = Reviews.objects.get(phone_number=pk)
    if request.method == "POST":
        reviews.delete()
        return redirect('dashboard')
    context = {'item': reviews}
    return render(request, 'Accounts/delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def staff_profile(request):
    user = request.user
    password_form = PasswordChangeForm(user)
    profile_form = EditProfileForm(instance=user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = EditProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('staff_profile')

        # Handle password updates
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Keep the user logged in after password change
                update_session_auth_hash(request, user)
                return redirect('staff_profile')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'user': user,
    }

    return render(request, 'Accounts/staff_profile.html', context)
