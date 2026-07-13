from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'age', 'gender', 'created_at')
    list_filter = ('gender',)
    search_fields = ('full_name', 'user__email')
    readonly_fields = ('created_at',)
