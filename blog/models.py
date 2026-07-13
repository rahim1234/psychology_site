from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=300, verbose_name='عنوان')
    content = models.TextField(verbose_name='محتوا')
    image = models.ImageField(upload_to='blog/images/', blank=True, null=True, verbose_name='تصویر')
    published = models.BooleanField(default=False, verbose_name='منتشر شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
