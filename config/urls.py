from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, BlogSitemap, BlogListSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
    'blog_list': BlogListSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('profile/', include('profiles.urls')),
    path('assessments/', include('assessments.urls')),
    path('blog/', include('blog.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('captcha/', include('captcha.urls')),
    # robots.txt 
    path('robots.txt', TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain"
    ), name='robots'),   
    
    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]

# ============================================================================
# 🔒 Custom Error Handlers
# ============================================================================
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
handler403 = 'core.views.custom_403'
handler400 = 'core.views.custom_400'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
