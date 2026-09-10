from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class FinalExam(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='final_exam')
    duration_minutes = models.PositiveIntegerField(default=30)
    pass_percentage = models.PositiveIntegerField(default=50)
    shuffle_questions = models.BooleanField(default=True)

    def __str__(self):
        return f"Final Exam - {self.course.title}"


class ExamQuestion(models.Model):
    exam = models.ForeignKey(FinalExam, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text[:50]


class ExamChoice(models.Model):
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(FinalExam, on_delete=models.CASCADE)
    score_percent = models.FloatField()
    passed = models.BooleanField(default=False)
    taken_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.course.title} - {self.score_percent}%"
