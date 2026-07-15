from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.ProfileCreateView.as_view(), name='profile_create'),
    path('update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('', views.DashboardView.as_view(), name='profile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('files/<str:kind>/<int:pk>/', views.protected_media, name='protected_media'),
]
