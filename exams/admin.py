from django.contrib import admin
from .models import FinalExam, ExamQuestion, ExamChoice, ExamResult


class ExamChoiceInline(admin.TabularInline):
    model = ExamChoice
    extra = 4


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam')
    inlines = [ExamChoiceInline]


@admin.register(FinalExam)
class FinalExamAdmin(admin.ModelAdmin):
    list_display = ('course', 'duration_minutes', 'pass_percentage')


admin.site.register(ExamResult)
