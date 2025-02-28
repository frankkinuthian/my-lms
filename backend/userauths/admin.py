from django.contrib import admin
from .models import User, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'date')

# Register your models here.
admin.site.register(User)
admin.site.register(Profile, ProfileAdmin)
