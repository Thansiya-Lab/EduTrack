from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Enrollment
from quizzes.models import QuizAttempt
from exams.models import ExamResult


@login_required
def student_progress(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    data = []
    all_scores = []
    quizzes_taken = 0
    exams_passed = 0
    courses_completed = 0

    for e in enrollments:
        total_modules = e.course.modules.count()
        quiz_attempts = list(
            QuizAttempt.objects.filter(
                student=request.user, quiz__module__course=e.course
            ).select_related('quiz')
        )
        exam_result = ExamResult.objects.filter(
            student=request.user, exam__course=e.course
        ).order_by('-taken_on').first()

        # best attempt per quiz -> how many quizzes are cleared
        best = {}
        for a in quiz_attempts:
            if a.quiz_id not in best or a.score_percent > best[a.quiz_id].score_percent:
                best[a.quiz_id] = a
        quizzes_passed = sum(1 for a in best.values() if a.score_percent >= a.quiz.pass_percentage)
        percent = min(100, round(quizzes_passed * 100 / total_modules)) if total_modules else 0

        exam_passed = bool(exam_result and exam_result.passed)
        if exam_passed:
            exams_passed += 1
            courses_completed += 1
            percent = 100
            status = 'completed'
        elif quiz_attempts or exam_result:
            status = 'in_progress'
        else:
            status = 'not_started'

        quizzes_taken += len(quiz_attempts)
        all_scores.extend(a.score_percent for a in quiz_attempts)

        data.append({
            'course': e.course,
            'total_modules': total_modules,
            'quiz_attempts': quiz_attempts,
            'quizzes_passed': quizzes_passed,
            'percent': percent,
            'status': status,
            'exam_result': exam_result,
        })

    summary = {
        'courses': len(data),
        'completed': courses_completed,
        'quizzes_taken': quizzes_taken,
        'avg_score': round(sum(all_scores) / len(all_scores)) if all_scores else 0,
        'exams_passed': exams_passed,
    }
    return render(request, 'progress_tracker/progress.html', {'data': data, 'summary': summary})
