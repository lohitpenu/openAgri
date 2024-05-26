from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import ApiKey

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('contact',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ApiKey)
