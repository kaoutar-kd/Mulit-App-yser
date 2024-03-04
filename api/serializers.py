from django.forms import ValidationError
from rest_framework import serializers
from .models import User,Image, SubscriptionPlan
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
    def validate(self, attrs):
        role = attrs.get('role', '')
        username = attrs.get('username', '')
        print(username.isalnum())
        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        allowed_roles = ['beta_player', 'company_user', 'growth_plan_subscriber']
        print(1, role)
        if role not in allowed_roles:
            raise ValidationError(f"Invalid role. Allowed roles are {', '.join(allowed_roles)}")
        return attrs
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['uploaded_by', 'image_file', 'description']
        
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'