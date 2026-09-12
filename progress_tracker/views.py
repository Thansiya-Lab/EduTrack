from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Enrollment
from quizzes.models import QuizAttempt
from exams.models import ExamResult


@login_required
def student_progress(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    data = []
    for e in enrollments:
        total_modules = e.course.modules.count()
        quiz_attempts = QuizAttempt.objects.filter(
            student=request.user, quiz__module__course=e.course
        )
        exam_result = ExamResult.objects.filter(
            student=request.user, exam__course=e.course
        ).order_by('-taken_on').first()

        data.append({
            'course': e.course,
            'total_modules': total_modules,
            'quiz_attempts': quiz_attempts,
            'exam_result': exam_result,
        })
    return render(request, 'progress_tracker/progress.html', {'data': data})
