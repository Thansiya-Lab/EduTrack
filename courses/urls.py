from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.enroll, name='enroll'),
    path('module/<int:module_id>/mark-watched/', views.mark_video_watched, name='mark_video_watched'),
]
