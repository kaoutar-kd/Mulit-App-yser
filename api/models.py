from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from rest_framework_simplejwt.tokens import RefreshToken

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=50, blank=True, null=True) 
    username = models.CharField(max_length=255, unique=True)
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
