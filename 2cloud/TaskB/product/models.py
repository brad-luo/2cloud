from django.db import models
from django.contrib.auth.models import User
from misc import SIZE_CHOICES, COLOR_CHOICES


# Create your models here.
class Product(models.Model):
    # link to user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(choices=COLOR_CHOICES, max_length=16, null=True, blank=True)
    size = models.CharField(choices=SIZE_CHOICES, max_length=16, null=True, blank=True)
    image = models.ImageField(upload_to='product_image', null=True, blank=True)

    def __str__(self):
        return self.name
