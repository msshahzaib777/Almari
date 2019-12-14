from django.db import models

# Create your models here.
class product(models.Model):
    title = models.CharField(max_length=500)
    price = models.CharField(max_length=5)
    imglink = models.CharField(max_length=500)
    link = models.CharField(max_length=500)

class fav(models.Model):
    user = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    price = models.CharField(max_length=5)
    imglink = models.CharField(max_length=500)
    link = models.CharField(max_length=500)
    abs = models.DecimalField(max_digits=7, decimal_places=2)
    theme = models.CharField(max_length=30)
    json = models.CharField(max_length=500)


class profile(models.Model):
    user = models.CharField(max_length=500)
    profilepic = models.ImageField()
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)