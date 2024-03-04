from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    role = models.CharField(primary_key=True, max_length=50)

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='./images/', default="")
    description = models.TextField(blank=True)

class SubscriptionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    features = models.TextField()
    benefits = models.TextField()
