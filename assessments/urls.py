from django.urls import path
from . import views

urlpatterns = [
    # ===== آزمون‌های قبلی =====
    path('phq-9/', views.PHQ9TestView.as_view(), name='phq9_test'),
    path('phq-9/result/<int:pk>/', views.PHQ9ResultDetailView.as_view(), name='phq9_result_detail'),
    
    path('gad-7/', views.GAD7TestView.as_view(), name='gad7_test'),
    path('gad-7/result/<int:pk>/', views.GAD7ResultDetailView.as_view(), name='gad7_result_detail'),
    
    path('history/', views.TestHistoryView.as_view(), name='test_history'),

    # ===== آزمون‌های جدید =====
    path('bdi-2/', views.BDITestView.as_view(), name='bdi_test'),
    path('bdi-2/result/<int:pk>/', views.BDIResultDetailView.as_view(), name='bdi_result_detail'),
    
    path('bai/', views.BAITestView.as_view(), name='bai_test'),
    path('bai/result/<int:pk>/', views.BAIResultDetailView.as_view(), name='bai_result_detail'),
    
    path('mcmi-4/', views.MCMI4TestView.as_view(), name='mcmi4_test'),
    path('mcmi-4/result/<int:pk>/', views.MCMI4ResultDetailView.as_view(), name='mcmi4_result_detail'),
]