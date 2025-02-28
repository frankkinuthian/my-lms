from django.shortcuts import render, get_object_or_404
from django.conf import settings
from api import serializer as api_serializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.response import Response
from userauths.models import User, Profile
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Any
import random

FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
OTP_LENGTH = 7

# Create your views here.

class MyTokenObtainPairView(TokenObtainPairView):
    """Custom token view that includes additional user information in the token."""
    serializer_class = api_serializer.MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    """View for registering new users."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer

#Random number generator for otp
def generate_random_otp(length: int = OTP_LENGTH) -> str:
    """Generate a random OTP of specified length."""
    otp = "".join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

class PasswordResetEmailVerifyAPIView(generics.GenericAPIView):
    """View for initiating the password reset process."""
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self) -> User:
        """Retrieve user by email from URL kwargs."""
        email = self.kwargs.get('email')
        return User.objects.filter(email=email).first()

    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """Handle GET request for password reset."""
        user = self.get_object()
        
        if not user:
            return Response(
                {"error": "No user found with this email address."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Generate tokens and OTP
            refresh = RefreshToken.for_user(user)
            user.otp = generate_random_otp()
            user.save()

            # Create reset link
            reset_link = (
                f"{FRONTEND_URL}/create-new-password/?"
                f"otp={user.otp}&"
                f"uuid={user.pk}&"
                f"refresh_token={str(refresh.access_token)}"
            )

            # TODO: Send email with reset link
            print(f"Reset link: {reset_link}")  # For development only

            return Response({
                "message": "Password reset link generated successfully",
                "reset_link": reset_link  # Remove in production
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Failed to generate reset link. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordChangeAPIView(generics.GenericAPIView):
    """View for changing password using OTP."""
    serializer_class = api_serializer.UserSerializer
    permission_classes = [AllowAny]

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """Handle POST request for password change."""
        try:
            # Extract data from request
            otp = request.data.get('otp')
            uuid = request.data.get('uuidb64')
            password = request.data.get('password')

            # Validate required fields
            if not all([otp, uuid, password]):
                return Response({
                    "error": "Missing required fields"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get user and validate OTP
            try:
                user = get_object_or_404(User, id=uuid, otp=otp)
            except User.DoesNotExist:
                return Response({
                    "error": "Invalid reset token or OTP"
                }, status=status.HTTP_404_NOT_FOUND)

            # Change password and clear OTP
            user.set_password(password)
            user.otp = ""
            user.save()

            return Response({
                "message": "Password changed successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Failed to change password. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
