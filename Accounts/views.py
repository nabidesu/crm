import subprocess
from pydub import AudioSegment
from django.core.files.uploadedfile import InMemoryUploadedFile
import json
import os
from urllib import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncWeek
from datetime import datetime

from crm import settings
from .models import *
from .form import *
from .utils import clean_data
from .filters import *
from .authentication import unauthenticated_user, allowed_users
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
import random
import string
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
import pickle

import whisper
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import io
import soundfile as sf
import numpy as np
os.environ["FFMPEG_BINARY"] = r"D:\ffmpeg\ffmpeg\bin\ffmpeg.exe"
os.environ["FFPROBE_BINARY"] = r"D:\ffmpeg\ffmpeg\bin\ffprobe.exe"
# Additional NLP imports
AudioSegment.converter = r"D:\ffmpeg\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"D:\ffmpeg\ffmpeg\bin\ffprobe.exe"


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
            Activity.objects.create(
                user=user,
                activity_type='register',
                description=f"{user.username} was registered."
            )

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
            Activity.objects.create(
                user=user,
                activity_type='login',
                description=f"{user.username} logged in."
            )
            messages.success(request, "Login successful!")
            return redirect('dashboard')

        else:
            messages.error(
                request, "Please check your username or password again.")

    # context = {}
    return render(request, 'Accounts/login.html')


def logoutUser(request):

    user = request.user
    logout(request)
    Activity.objects.create(
        user=user,
        activity_type='logout',
        description=f"{user.username} logged out."
    )
    return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def main(request):
    users = User.objects.all()
    reviews = Reviews.objects.filter(responseAlert=True).values(
        'email', 'review', 'created_at')
    activities = Activity.objects.all().order_by('-timestamp')[:10]
    context = {
        'users': users,
        'activities': activities,
        'reviews': reviews,
    }
    return render(request, 'Accounts/main.html', context)


os.environ["PATH"] += os.pathsep + os.path.dirname(r"D:\ffmpeg\ffmpeg\bin")
# Load Whisper model
# You can use "small", "medium", or "large" for better accuracy
whisper_model = whisper.load_model("base")


def process_audio(audio_file):
    """Convert voice recording to text using Whisper model."""
    try:
        # Ensure we're at the start of the file
        audio_file.seek(0)

        # Create a temporary file for the original audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            for chunk in audio_file.chunks():
                tmp_file.write(chunk)
            original_path = tmp_file.name

        print(f"Original file created at: {original_path}")

        # Create a path for the converted file
        converted_path = original_path + ".pcm.wav"

        # Convert using explicit ffmpeg path
        ffmpeg_path = r"D:\ffmpeg\ffmpeg\bin\ffmpeg.exe"
        cmd = [
            ffmpeg_path, "-y",
            "-i", original_path,
            "-f", "s16le",
            "-ac", "1",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            converted_path
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
            print(f"Conversion successful, output file: {converted_path}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            raise

        # Now manually load the audio using numpy
        audio_data = np.fromfile(
            converted_path, np.int16).astype(np.float32) / 32768.0

        # Process with Whisper, bypassing its load_audio function
        transcription = whisper_model.transcribe(audio_data)
        transcribed_text = transcription["text"].strip()

        # Clean up
        try:
            os.unlink(original_path)
            os.unlink(converted_path)
        except Exception as e:
            print(f"Warning: Could not delete temp files: {e}")

        return transcribed_text

    except Exception as e:
        print(f"Audio processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""


# For model loading
tfidf_path = os.path.join(settings.BASE_DIR, 'Accounts',
                          'ml_models', 'tfidf_vectorizer.pkl')
model_path = os.path.join(settings.BASE_DIR, 'Accounts',
                          'ml_models', 'voting_classifier_model.pkl')

with open(tfidf_path, 'rb') as file:
    tfidf_vectorizer = pickle.load(file)

with open(model_path, 'rb') as file:
    voting_clf = pickle.load(file)


# def predict_emotion(text):

#     try:
#         if not isinstance(text, str):
#             text = str(text)
#         if not text.strip():
#             return "unknown"

#         clean_text = clean_data(text)
#         print(f"Original text: {text}")
#         print(f"Cleaned text: {clean_text}")
#         text_vector = tfidf_vectorizer.transform([clean_text])
#         prediction = voting_clf.predict(text_vector)
#         mapping = {1: "positive", 0: "neutral", -1: "negative"}
#         predicted_emotion = mapping.get(prediction[0], "unknown")
#         print(f"Predicted emotion: {predicted_emotion}")
#         return predicted_emotion
#     except Exception as e:
#         print(f"Error in predict_emotion: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return "unknown"

def predict_emotion(user_input):
    clean_input = clean_data(user_input)
    user_input_tfidf = tfidf_vectorizer.transform([clean_input])
    prediction = voting_clf.predict(user_input_tfidf)
    predicted_emotion = prediction[0]
    return predicted_emotion


# @allowed_users(allowed_roles=['admin', 'customer'])
def give_review(request):
    form = ReviewForm()

    if request.method == "POST":
        # Make sure to include request.FILES
        form = ReviewForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            responseAlert = form.cleaned_data.get('responseAlert')
            review_text = ""

            # Process audio file if uploaded
            if 'audio' in request.FILES and request.FILES['audio']:
                review_text = process_audio(request.FILES['audio'])
                if not review_text:
                    messages.error(
                        request, "Could not process audio recording.")
                    return render(request, "Accounts/give_review.html", {"form": form})

            # Use text review if no audio or audio failed
            if not review_text:
                review_text = form.cleaned_data.get('review')
                if not review_text:
                    messages.error(
                        request, "Please provide either a text or audio review.")
                    return render(request, "Accounts/give_review.html", {"form": form})

            # Look up the customer using the provided email
            try:
                customer = Customer.objects.get(
                    customerEmail=email, activityStatus=1)

            except Customer.DoesNotExist:
                messages.error(
                    request, "This email is not registered. Please register your account through the reception.")
                return render(request, "Accounts/give_review.html", {"form": form})

            # Check that the review window is still open (if verified_at is set)

            if customer.verified_at:
                allowed_review_period = customer.verified_at + \
                    timezone.timedelta(days=customer.noOfDays + 1)

                if timezone.now() > allowed_review_period:

                    messages.error(
                        request,
                        "The allowed review period has ended. Your token has expired."
                    )
                    return render(request, "Accounts/give_review.html", {"form": form})

            # Check if the customer has already submitted 2 reviews
            # reviews_count = Reviews.objects.filter(
            #     email=customer.customerEmail).count()
            # print("Existing review count for this customer:", reviews_count)
            # if reviews_count >= 2:
            #     messages.error(
            #         request,
            #         "You have already submitted the maximum allowed reviews."
            #     )
            #     return render(request, "Accounts/give_review.html", {"form": form})

            # Create the review and assign the respective customer (linking via the foreign key)
            try:
                new_review = Reviews.objects.create(
                    review=review_text,
                    emotion=predict_emotion(review_text),
                    responseAlert=responseAlert,
                    email=email  # This links the review to the customer instance
                )
                new_review.save()
                print("Review created successfully.")

            except Exception as e:
                print("Error saving review:", e)
            messages.success(request, "Review submitted successfully!")

            # Redirect to a confirmation page or dashboard
            return redirect('dashboard')

        else:
            print("Form is not valid:", form.errors)
            messages.error(request, "Please correct the errors below.")

    reviews = Reviews.objects.filter(
        emotion="positive").order_by('-created_at')[:5]
    context = {'reviews': reviews, 'form': form}

    return render(request, 'Accounts/give_review.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff'])
def dashboard(request):
    # Start with all reviews
    reviews = Reviews.objects.all()

    # Apply the filter first
    myFilter = ReviewFilter(request.GET, queryset=reviews)
    filtered_reviews = myFilter.qs

    # Then apply limit to the filtered reviews
    limit = request.GET.get('limit', 'all')
    display_reviews = filtered_reviews

    if limit != 'all':
        try:
            limit_val = int(limit)
            # Order by creation date (newest first) before limiting
            display_reviews = filtered_reviews.order_by(
                '-created_at')[:limit_val]
        except ValueError:
            # If limit is not a valid integer, ignore it
            pass

    # Calculate emotion counts based on the filtered reviews (not limited ones)
    emotion_counts = {
        'positive': filtered_reviews.filter(emotion='positive').count(),
        'negative': filtered_reviews.filter(emotion='negative').count(),
        'neutral': filtered_reviews.filter(emotion='neutral').count(),
        'unknown': filtered_reviews.filter(emotion='unknown').count(),
    }

    # Categories calculation based on filtered reviews
    categories = {
        'Service': ['service', 'support', 'help', 'assist', 'staff'],
        'Food': ['food', 'meal', 'dish', 'taste', 'yummy'],
        'Experience': ['experience', 'visit', 'time', 'trip'],
        'Ambience': ['ambience', 'atmosphere', 'vibe', 'environment'],
        'Hygiene': ['hygiene', 'clean', 'sanitary', 'cleanliness', 'dirty'],
        'Price': ['price', 'cost', 'expensive', 'cheap', 'costly'],
    }

    category_counts = {category: 0 for category in categories}

    # Count occurrences of each category-related word in the filtered reviews
    for review in filtered_reviews:
        # Convert review text to lowercase for case-insensitive matching
        review_text = review.review.lower()
        for category, keywords in categories.items():
            category_counts[category] += sum(
                keyword in review_text for keyword in keywords)

    context = {
        'reviews': display_reviews,
        'myFilter': myFilter,
        'emotion_counts': emotion_counts,
        'category_counts': category_counts,
    }

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
    try:
        reviews = Reviews.objects.get(reviewID=pk)
    except Reviews.DoesNotExist:
        raise Http404("Review not found.")

    if request.method == "POST":
        reviews.delete()
        return redirect('dashboard')
    context = {'item': reviews}
    return render(request, 'Accounts/delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff'])
def removeCustomer(request, pk):
    try:
        customers = Customer.objects.get(customerEmail=pk)
    except Customer.DoesNotExist:
        raise Http404("Customer not found.")

    if request.method == "POST":
        customers.delete()
        return redirect('customer_info')
    context = {'item': customers}
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


def send_verification_email(request, customer):
    verification_token = get_random_string(length=32)
    customer.verification_token = verification_token
    customer.save()
    # base_url = request.scheme + "://" + request.get_host()
    # base_url = 'http://127.0.0.1:8000'
    # verification_link = f"{base_url}/verify-email/{verification_token}/"
    base_url = request.scheme + "://" + request.get_host()
    verification_link = base_url + \
        reverse('verify_customer', args=[verification_token])

    send_mail('Verify your account for registration',
              f'Please click here to verify your account:{verification_link}',
              'Hotelmanager1302@gmail.com',
              [customer.customerEmail],
              fail_silently=False,)


def register_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.email_verified = False

            customer.adminUserID = request.user

            customer.save()

            send_verification_email(request, customer)
            messages.success(
                request, f'Verification email is sent to {customer.customerEmail}.')
            return redirect('dashboard')
    else:
        form = CustomerForm()
    return render(request, 'Accounts/customer_registration.html', {'form': form})


def generate_token():
    characters = string.ascii_letters + string.digits
    while True:
        token = ''.join(random.choices(characters, k=8))
        if not Customer.objects.filter(tokenNumber=token).exists():
            return token


def update_customer_status(customer):
    allowed_review_period = None

    # Check if customer.verified_at is not None before calculating allowed review period
    if customer.verified_at:
        allowed_review_period = customer.verified_at + \
            timezone.timedelta(days=customer.noOfDays + 1)
        is_valid = timezone.now() <= allowed_review_period
    else:
        # If verified_at is None, mark the status as invalid
        is_valid = False

    # Create or update the customer's status object
    status_obj, _ = Status.objects.get_or_create(customerEmail=customer)
    status_obj.deliveryStatus = 'delivered'
    status_obj.isValid = is_valid
    status_obj.save()

    return status_obj


def verify_customer(request, verification_token):
    customer = get_object_or_404(
        Customer, verification_token=verification_token, email_verified=False)

    customer.email_verified = True
    customer.verified_at = timezone.now()  # Set the verified date
    if customer.tokenNumber == '':
        customer.tokenNumber = generate_token()  # Generate token Now
    customer.activityStatus = 1  # Activate the customer
    customer.verification_token = None  # clear token

    # Save the updated customer record
    customer.save()

    # Create or update the Status record for this customer
    update_customer_status(customer)

    # Send success message and redirect to confirmation page
    messages.success(
        request, 'Success! Your account is verified, and you can now give a review.')
    return redirect('confirmation')


def confirmation_page(request):
    return render(request, 'Accounts/confirmation_page.html')


def customer_info(request):
    customers = Customer.objects.all()
    status = Status.objects.all()
    customer_filter = CustomerFilter(request.GET, queryset=customers)
    status_filter = StatusFilter(request.GET, queryset=status)

    # Sorting
    sort_by_customer = request.GET.get('sort_customer', '')
    sort_by_status = request.GET.get('sort_status', '')

    if sort_by_customer:
        customers = customer_filter.qs.order_by(sort_by_customer)
    else:
        customers = customer_filter.qs

    if sort_by_status:
        status = status_filter.qs.order_by(sort_by_status)
    else:
        status = status_filter.qs

    # Update each customer's status validity dynamically
    for customer in customers:
        update_customer_status(customer)

    weekly_info = (
        Customer.objects.values(week=TruncWeek('verified_at'))
        .annotate(count=Count('customerEmail')).order_by('week')
    )
    weeks = []
    counts = []
    for entry in weekly_info:
        if entry['week']:
            weeks.append(
                f"Week {entry['week'].isocalendar()[1]}, {entry['week'].year}")
            counts.append(entry['count'])
    context = {
        'customers': customers,
        'status': status,
        'customer_filter': customer_filter,
        'status_filter': status_filter,
        'weeks_json': json.dumps(weeks),
        'counts_json': json.dumps(counts),
    }
    return render(request, 'Accounts/customer_info.html', context)


def log_activity(request, message):
    if 'recent_activties' not in request.session:
        request.session['recent_activties'] = []
    request.session['recent_activties'].insert(0, message)
    request.session['recent_activties'] = request.session['recent_activties'][:5]
    request.session.modified = True
