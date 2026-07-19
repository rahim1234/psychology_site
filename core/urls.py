from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),

    # پنل ساده‌ی مدیریت محتوای سایت (فقط سوپریوزر)
    path('manage/content/', views.ManageContentView.as_view(), name='manage_content'),
]
