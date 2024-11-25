from django.db import models

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    data_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class reviews (models.Model):
    review = models.CharField(max_length=5000)
    data_created = models.DateTimeField(auto_now_add=True, null=True)


class customer_reviews(models.Model):
    STATUS = (('Pending', 'Pending'), ('Reviewed', 'Reviewed'))

    status = models.CharField(max_length=5000, choices=STATUS)
    # customer=
    # reviews=
    data_created = models.DateTimeField(auto_now_add=True, null=True)
