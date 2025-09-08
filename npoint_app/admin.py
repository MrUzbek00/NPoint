from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, JSONData, PasswordResetCode

@admin.register(UserProfile)
class CustomUserAdmin(UserAdmin):
    model = UserProfile
    list_display = ("username", "email", "first_name", "last_name", "is_staff", 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    


@admin.register(JSONData)
class JSONDataAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_public", "created_at", "updated_at", "access_count")
    search_fields = ('title', 'user__username', 'description')
    list_filter = ('is_public', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "reset_code", "created_at", "is_used")
    search_fields = ('user__username', 'reset_code')
    list_filter = ('is_used', 'created_at')
    ordering = ('-created_at',)