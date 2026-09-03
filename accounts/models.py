from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    STATUS_CHOICES = (
        ('student', 'Student'),
        ('working', 'Working Professional'),
        ('job_seeker', 'Job Seeker'),
        ('other', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='student')

    def __str__(self):
        return self.full_name
