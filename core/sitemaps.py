from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post


class StaticViewSitemap(Sitemap):
    """Sitemap برای صفحات استاتیک (home, about, contact)"""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return ['home', 'about', 'contact']
    
    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    """Sitemap برای مقالات وبلاگ"""
    changefreq = 'weekly'
    priority = 0.9
    
    def items(self):
        return Post.objects.filter(published=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f'/blog/{obj.pk}/'


class BlogListSitemap(Sitemap):
    """Sitemap برای لیست مقالات"""
    priority = 0.7
    changefreq = 'daily'
    
    def items(self):
        return ['blog_list']
    
    def location(self, item):
        return reverse(item)