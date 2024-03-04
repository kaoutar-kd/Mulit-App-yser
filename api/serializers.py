from django.forms import ValidationError
from rest_framework import serializers
from .models import User,Image, SubscriptionPlan
from rest_framework import serializers
from django.contrib.auth.models import User as User_auth
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    class Meta:
        model = User
        fields = ['role', 'username', 'password', 'id']
    def validate(self, attrs):
        role = attrs.get('role', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        allowed_roles = ['beta_player', 'company_user', 'growth_plan_subscriber']
        if role not in allowed_roles:
            raise ValidationError(f"Invalid role. Allowed roles are {', '.join(allowed_roles)}")
        return attrs
    def create(self, validated_data):
        user = User_auth.objects.create_user({'username':validated_data['username'], 'password':validated_data['password']})
        print(f"Users created: {User_auth.objects.all()}")
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(username=obj['username'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['password', 'username', 'tokens']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        user = authenticate(username=username, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')

        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            'role': user.role,
            'username': user.username,
            'tokens': user.tokens()  
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['uploaded_by', 'image_file', 'description']
        
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'