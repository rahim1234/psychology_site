from django.urls import path
from . import views

urlpatterns = [
    path('phq-9/', views.PHQ9TestView.as_view(), name='phq9_test'),
    path('phq-9/result/<int:pk>/', views.PHQ9ResultDetailView.as_view(), name='phq9_result_detail'),
    path('gad-7/', views.GAD7TestView.as_view(), name='gad7_test'),
    path('gad-7/result/<int:pk>/', views.GAD7ResultDetailView.as_view(), name='gad7_result_detail'),
    path('history/', views.TestHistoryView.as_view(), name='test_history'),
]
