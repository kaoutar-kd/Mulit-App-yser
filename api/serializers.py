from django.forms import ValidationError
from rest_framework import serializers
from .models import Role, User,Image, SubscriptionPlan
from rest_framework import serializers
from django.contrib.auth.models import User as User_auth
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())  # Adjust the queryset accordingly

    def validate(self, attrs):
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                "Username must contain only letters and numbers.")

        return attrs

    def create(self, validated_data):
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
    class Meta:
        model = Role
        fields = ['role']
    def validate_role(self, value):
        allowed_roles = ['beta_player', 'company_user', 'growth_plan_subscriber']

        if value not in allowed_roles:
            raise serializers.ValidationError(f"Invalid role. Allowed roles are {', '.join(allowed_roles)}")

        return value
 
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'uploaded_by', 'image_file', 'description']
        
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'