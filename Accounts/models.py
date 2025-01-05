from django.db import models

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Positive_reviews (models.Model):
    review = models.CharField(max_length=5000)
    STATUS = (('Pending', 'Pending'), ('Reviewed', 'Reviewed'))

    status = models.CharField(max_length=5000, choices=STATUS)


class Negative_reviews(models.Model):
    STATUS = (('Pending', 'Pending'), ('Reviewed', 'Reviewed'))

    status = models.CharField(max_length=5000, choices=STATUS)
