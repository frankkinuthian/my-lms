from django.shortcuts import render
from api import serializer as api_serializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.response import Response
from userauths.models import User, Profile
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import random

FRONTEND_URL = "http://localhost:5173"

# Create your views here.

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer

#Random number generator for otp
def generate_random_otp(length=7):
    otp = "".join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

class PasswordResetEmailVerifyAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs.get('email')
        user = User.objects.filter(email=email).first()
        return user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        
        if not user:
            return Response(
                {"error": "No user found with this email address."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate uuidb64
        uuidb64 = user.pk
        # Generate refresh token
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh.access_token)
        # Generate otp
        user.otp = generate_random_otp()
        user.save()

        link = f"{FRONTEND_URL}/create-new-password/?otp={user.otp}&uuid={uuidb64}&refresh_token={refresh_token}"
        print("link =====>", link)

        return Response({
            "message": "Password reset link generated successfully",
            "reset_link": link
        }, status=status.HTTP_200_OK)

