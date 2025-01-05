from django.contrib import admin

# Register your models here.
from .models import Customer, Positive_reviews, Negative_reviews
admin.site.register(Customer)
admin.site.register(Negative_reviews)
admin.site.register(Positive_reviews)
