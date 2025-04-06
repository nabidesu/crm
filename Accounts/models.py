

from sqlite3.dbapi2 import Timestamp
from django.db import models

from django.contrib.auth.models import User
# Create your models here.


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='staff_profiles/', null=True, blank=True)


class Customer(models.Model):
    ROOM_CHOICES = [
        ('single', 'Single Room'),
        ('deluxe', 'Deluxe Room'),
        ('double', 'Double Room'),
    ]

    ROOM_PRICES = {
        'single': 1500,
        'deluxe': 3000,
        'double': 2000,
    }
    customerEmail = models.EmailField(
        max_length=100, null=False, primary_key=True)
    roomType = models.CharField(
        max_length=50, choices=ROOM_CHOICES, null=False, default='double')
    noOfDays = models.PositiveIntegerField(null=False)
    charge = models.DecimalField(
        max_digits=10, null=False, decimal_places=2,  blank=True, default=0)
    activityStatus = models.IntegerField(null=False, default=0)
    tokenNumber = models.CharField(
        max_length=10, unique=True, editable=False, default='', blank=True)
    email_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    adminUserID = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    verification_token = models.CharField(max_length=32, blank=True, null=True)

    def save(self, *args, **kwargs):
        """Automatically calculate total charge based on room type and days."""
        self.charge = self.noOfDays * self.ROOM_PRICES.get(self.roomType, 0)
        super().save(*args, **kwargs)


class Reviews(models.Model):
    reviewID = models.AutoField(primary_key=True)
    review = models.TextField(null=False)
    emotion = models.CharField(max_length=50, null=True, default='neutral')
    created_at = models.DateTimeField(auto_now_add=True)
    responseAlert = models.BooleanField(default=False)
    email = models.EmailField()


class Status(models.Model):
    statusID = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    deliveryStatus = models.CharField(max_length=50,
                                      choices=[('delivered', 'Delivered'), ('failed', 'Failed')])
    isValid = models.BooleanField(default=True)
    customerEmail = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('register', 'User Registered'),
        ('login', 'User Logged In'),
        ('logout', 'User Logged Out'),
        ('review', 'Review Submitted'),
        ('other', 'Other Activity'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(default=Timestamp.now)
