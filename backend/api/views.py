from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from api import serializer as api_serializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.response import Response
from userauths.models import User, Profile
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Any, Tuple
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

    def send_reset_email(self, user: User, reset_link: str) -> Tuple[bool, str]:
        """
        Send password reset email using Anymail/Mailgun.
        """
        try:
            # Prepare email content
            context = {
                'user': user,
                'reset_link': reset_link,
                'frontend_url': FRONTEND_URL,
            }
            
            # Debug template rendering
            html_content = render_to_string(
                'email/password_reset.html',
                context
            )
            print("Template rendered successfully")
            
            text_content = strip_tags(html_content)
            print("Text content created")
            
            try:
                # Get Mailgun domain from settings
                mailgun_domain = settings.ANYMAIL.get('MAILGUN_SENDER_DOMAIN')
                from_email = f"Frank's LMS <mailgun@{mailgun_domain}>"
                
                # Create message
                msg = EmailMultiAlternatives(
                    subject="Password Reset Request",
                    body=text_content,
                    from_email=from_email,  # Use the constructed from_email
                    to=[user.email],
                    headers={  # Add Mailgun-specific headers
                        "X-Mailgun-Variables": {
                            "user_id": str(user.id),
                            "reset_type": "password"
                        }
                    }
                )
                print(f"Email message created with from_email: {from_email}")
                
                msg.attach_alternative(html_content, "text/html")
                print("HTML content attached")
                
                # Debug Mailgun settings
                print(f"Mailgun API Key: {settings.ANYMAIL.get('MAILGUN_API_KEY')[:6]}...")
                print(f"Mailgun Domain: {mailgun_domain}")
                
                # Send with explicit configuration
                msg.send(fail_silently=False)
                print("Email sent successfully")
                return True, ""
                
            except Exception as email_error:
                print(f"Email sending error: {str(email_error)}")
                import traceback
                print(traceback.format_exc())
                return False, str(email_error)
            
        except Exception as e:
            print(f"General error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False, str(e)

    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """Handle GET request for password reset."""
        try:
            user = self.get_object()
            
            if not user:
                return Response(
                    {"error": "No user found with this email address."},
                    status=status.HTTP_404_NOT_FOUND
                )

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

            # Send email with detailed error handling
            email_sent, error_message = self.send_reset_email(user, reset_link)
            print(f"Email sending result: {email_sent}, Error: {error_message}")
            
            if email_sent:
                return Response({
                    "message": "Password reset instructions have been sent to your email.",
                    "email": user.email
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": f"Failed to send reset email: {error_message}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"View error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response({
                "error": f"Failed to process reset request: {str(e)}"
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
