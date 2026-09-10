from django.urls import path
from . import views

urlpatterns = [
    path('<int:exam_id>/', views.take_exam, name='take_exam'),
    path('certificate/<int:result_id>/', views.download_certificate, name='download_certificate'),
]
