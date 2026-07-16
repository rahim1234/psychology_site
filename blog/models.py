from django.conf import settings
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField  # اضافه شود

class Post(models.Model):
    title = models.CharField(max_length=300, verbose_name='عنوان')
    
    # تغییر این خط:
    content = RichTextUploadingField(verbose_name='محتوا')
    
    image = models.ImageField(upload_to='blog/images/', blank=True, null=True, verbose_name='تصویر کاور')
    published = models.BooleanField(default=False, verbose_name='منتشر شده')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_posts',
        verbose_name='نویسنده',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title