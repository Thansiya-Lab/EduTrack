from django.urls import path
from . import views

urlpatterns = [
    path('<int:quiz_id>/', views.take_quiz, name='take_quiz'),
]
