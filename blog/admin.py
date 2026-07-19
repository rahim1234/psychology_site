from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'created_at')
    list_filter = ('published', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('published',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Only staff/admin accounts should be selectable as an article
        # author -- regular site visitors must never show up in this list.
        if db_field.name == 'author':
            kwargs['queryset'] = db_field.related_model.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
