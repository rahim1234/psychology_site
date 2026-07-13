from django.contrib import admin
from .models import PHQ9Result, GAD7Result


@admin.register(PHQ9Result)
class PHQ9ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'severity', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)


@admin.register(GAD7Result)
class GAD7ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'severity', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)
