from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    """
    Model representing user roles.

    Attributes:
        role (str): The role name (primary key).
    """
    role = models.CharField(primary_key=True, max_length=50)

class SubscriptionPlan(models.Model):
    """
    Model representing subscription plans.

    Attributes:
        subscription_plan (str): Subscription plan name.
        features (str): Features included in the subscription plan.
        benefits (str): Benefits of the subscription plan.
    """
    subscription_plan = models.CharField(primary_key=True, max_length=50)
    features = models.TextField()
    benefits = models.TextField()


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.

    Attributes:
        role (Role): ForeignKey relationship with the Role model.
        subscription_plan (SubscriptionPlan): ForeignKey relationship with the SubscriptionPlan model.
        username (str): User's unique username.
        password (str): User's password.
    """
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)

class Image(models.Model):
    """
    Model representing uploaded images.

    Attributes:
        uploaded_by (User): ForeignKey relationship with the User model.
        image_file (ImageField): Image file field.
        description (str): Image description (optional).
    """
    id = models.AutoField(primary_key=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image_file = models.ImageField(upload_to='./images/', default="")
    description = models.TextField(blank=True)