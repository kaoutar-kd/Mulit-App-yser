from django.forms import ValidationError
from rest_framework import serializers
from .models import Role, User, Image, SubscriptionPlan
from django.contrib.auth.models import User as User_auth
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Attributes:
        role: PrimaryKeyRelatedField for the User's role.
    """
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        """
        Validate the username to ensure it contains only letters and numbers.

        Args:
            attrs (dict): Dictionary of validated data.

        Returns:
            dict: Validated data.
        """
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                "Username must contain only letters and numbers.")

        return attrs

    def create(self, validated_data):
        """
        Create a new User instance.

        Args:
            validated_data (dict): Dictionary of validated data.

        Returns:
            User: Created User instance.
        """
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)

        try:
            role = Role.objects.get(role=role.role)
        except Role.DoesNotExist:
            raise ValidationError("Role with provided ID does not exist.")

        instance = self.Meta.model(role=role, **validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Role model.

    Attributes:
        validate_role: Custom validation for the 'role' field.
    """
    class Meta:
        model = Role
        fields = ['role']

    def validate_role(self, value):
        """
        Validate the 'role' field to ensure it is one of the allowed roles.

        Args:
            value: The value of the 'role' field.

        Returns:
            str: Validated 'role' value.
        """
        allowed_roles = ['beta_player', 'company_user', 'growth_plan_subscriber']

        if value not in allowed_roles:
            raise serializers.ValidationError(
                f"Invalid role. Allowed roles are {', '.join(allowed_roles)}")

        return value

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Attributes:
        role: PrimaryKeyRelatedField for the User's role.
    """
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'password', 'subscription_plan']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        """
        Validate the username to ensure it contains only letters and numbers.

        Args:
            attrs (dict): Dictionary of validated data.

        Returns:
            dict: Validated data.
        """
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                "Username must contain only letters and numbers.")

        return attrs

    def validate_subscription_plan(self, value):
        """
        Validate the subscription plan based on the user's role.

        Args:
            value (str): Input subscription plan.

        Returns:
            str: Validated subscription plan.

        Raises:
            serializers.ValidationError: If the role is 'growth_plan_subscriber' and subscription_plan is empty.
            serializers.ValidationError: If the role is not 'growth_plan_subscriber' and subscription_plan is provided.
        """
        if self.initial_data['role'] == 'growth_plan_subscriber' and not value:
            raise serializers.ValidationError("Subscription plan is required for 'growth_plan_subscriber'.")
        if self.initial_data['role'] != 'growth_plan_subscriber' and value:
            raise serializers.ValidationError("Subscription plan is only for 'growth_plan_subscriber'.")
        return value

    def create(self, validated_data):
        """
        Create a new User instance.

        Args:
            validated_data (dict): Dictionary of validated data.

        Returns:
            User: Created User instance.
        """
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)

        try:
            role = Role.objects.get(role=role.role)
        except Role.DoesNotExist:
            raise ValidationError("Role with provided ID does not exist.")

        instance = self.Meta.model(role=role, **validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance

class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Image model.
    """
    class Meta:
        model = Image
        fields = ['id', 'uploaded_by', 'image_file', 'description']

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    Serializer for the SubscriptionPlan model.
    """
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
