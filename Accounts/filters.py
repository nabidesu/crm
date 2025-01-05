import django_filters
from .models import Reviews
from django_filters import DateFromToRangeFilter, CharFilter, ChoiceFilter

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
