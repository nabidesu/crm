from django.db import models

# Create your models here.


class Reviews(models.Model):
    name = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(
        max_length=10, null=False, primary_key=True)
    review = models.TextField(null=False)
    emotion = models.CharField(max_length=50, null=True, default='neutral')
    created_at = models.DateTimeField(auto_now_add=True)
