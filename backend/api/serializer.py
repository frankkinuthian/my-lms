from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from typing import Any, Dict
from userauths.models import User, Profile

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes additional user information in the token."""
    
    @classmethod
    def get_token(cls, user: User) -> Dict[str, Any]:
        """Enhance the token with additional user data."""
        token = super().get_token(user)
        
        # Add custom claims
        token.update({
            'full_name': user.full_name,
            'email': user.email,
            'username': user.username,
        })
        
        return token


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password validation."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True}
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create a new user with the validated data."""
        # Remove password2 as it's not needed for user creation
        validated_data.pop('password2', None)
        
        user = User.objects.create(
            email=validated_data['email'],
            full_name=validated_data['full_name']
        )
        
        user.set_password(validated_data['password'])
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name')
        read_only_fields = ('id',)


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile model."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ('id', 'user', 'image', 'full_name', 'country', 'about', 'date')
        read_only_fields = ('id', 'date')

