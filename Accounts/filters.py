import django_filters
from .models import *
from django_filters import DateFromToRangeFilter, CharFilter, ChoiceFilter, BooleanFilter

CATEGORY = ('Positive', 'Negative', 'Neutral')


class ReviewFilter(django_filters.FilterSet):
    created_at = DateFromToRangeFilter(
        field_name='created_at', label='DATE-FROM-TO')

    review = CharFilter(field_name='review', lookup_expr='icontains')
    EMOTION_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    emotion = ChoiceFilter(
        field_name='emotion',
        label='Emotion',
        choices=EMOTION_CHOICES,

    )

    class Meta:
        model = Reviews
        fields = ['emotion', 'created_at', 'review']


class CustomerFilter(django_filters.FilterSet):
    customerEmail = CharFilter(
        field_name='customerEmail', lookup_expr='icontains', label='Email')
    tokenNumber = CharFilter(field_name='tokenNumber',
                             lookup_expr='icontains', label='Token Number')
    activityStatus = ChoiceFilter(field_name='activityStatus', choices=[
                                  (1, 'Active'), (0, 'Inactive')], label='Activity Status')

    email_verified = BooleanFilter(
        field_name='email_verified', label='Email Verified')
    responseAlert = ChoiceFilter(field_name='responseAlert', choices=[(
        'emergency', 'Emergency'), ('none', 'None')], label='Response Alert')

    class Meta:
        model = Customer
        fields = ['activityStatus', 'verified_at',
                  'email_verified', 'responseAlert']


class StatusFilter(django_filters.FilterSet):
    customerEmail = CharFilter(field_name='customerEmail__customerEmail',
                               lookup_expr='icontains', label='Customer Email')
    deliveryStatus = ChoiceFilter(field_name='deliveryStatus', choices=[(
        'delivered', 'Delivered'), ('failed', 'Failed')], label='Delivery Status')
    isValid = BooleanFilter(field_name='isValid', label='Is Valid')
    timestamp = DateFromToRangeFilter(
        field_name='timestamp', label='Timestamp Range')

    class Meta:
        model = Status
        fields = ['customerEmail', 'deliveryStatus', 'isValid', 'timestamp']
