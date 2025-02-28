from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from typing import Any
from django.db.models.signals import post_save
from django.dispatch import receiver

DEFAULT_USER_IMAGE = 'default-user.jpg'
MAX_NAME_LENGTH = 100
MAX_ABOUT_LENGTH = 500
OTP_LENGTH = 6

# Custom User model that extends Django's AbstractUser to add additional fields and functionality.
class User(AbstractUser):
    # Field to store the username, ensuring it is unique.
    username = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    # Field to store the email address, ensuring it is unique.
    email = models.EmailField(unique=True)
    # Field to store the full name of the user.
    full_name = models.CharField(max_length=MAX_NAME_LENGTH)
    # Field to store the OTP (One-Time Password) for additional security, can be null or blank.
    otp = models.CharField(max_length=OTP_LENGTH, null=True, blank=True)

    # Set email as the main field for authentication instead of the default username.
    USERNAME_FIELD = 'email'
    # Specify that the username is required when creating a user.
    REQUIRED_FIELDS = ['username']

    # String representation of the User model, returns the email address.
    def __str__(self) -> str:
        return self.email

    # Override the save method to automatically set the full_name and username if they are not provided.
    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.full_name:
            self.full_name = self.email.split('@')[0]
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)


class Profile(models.Model):
    # Represents a user profile linked to a User model instance.
    image = models.FileField(
        upload_to='user_folder',
        default=DEFAULT_USER_IMAGE,
        null=True,
        blank=True
    )
    # Use fileField because of diff extensions such as .heif etc that may not be jpeg or png
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=MAX_NAME_LENGTH)
    country = models.CharField(max_length=MAX_NAME_LENGTH, null=True, blank=True)
    about = models.TextField(max_length=MAX_ABOUT_LENGTH, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        # Returns the full name of the profile if available, otherwise returns the full name of the associated user.
        return self.full_name or self.user.full_name

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.full_name:
            self.full_name = self.user.username
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if self.about and len(self.about) > MAX_ABOUT_LENGTH:
            raise ValidationError({
                'about': f'About text cannot exceed {MAX_ABOUT_LENGTH} characters'
            })


@receiver(post_save, sender=User)
def create_user_profile(sender: type[User], instance: User, created: bool, **kwargs: Any) -> None:
    """
    Signal handler to create a Profile instance when a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender: type[User], instance: User, **kwargs: Any) -> None:
    """
    Signal handler to save the Profile instance whenever the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
