from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Enrollment
from courses.utils import get_module_lock_status
from .models import Quiz, QuizAttempt


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    module = quiz.module
    course = module.course

    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, 'You must enroll in this course before taking this quiz.')
        return redirect('course_detail', slug=course.slug)

    module_data, _ = get_module_lock_status(request.user, course)
    this_entry = next((m for m in module_data if m['module'].id == module.id), None)

    if not this_entry or not this_entry['quiz_accessible']:
        messages.error(request, 'Please watch the module video fully before attempting this quiz.')
        return redirect('course_detail', slug=course.slug)

    if request.method == 'POST':
        total = quiz.questions.count()
        correct = 0
        for q in quiz.questions.all():
            selected_id = request.POST.get(f'question_{q.id}')
            if selected_id:
                try:
                    choice = q.choices.get(id=selected_id)
                    if choice.is_correct:
                        correct += 1
                except Exception:
                    pass
        score = (correct / total) * 100 if total else 0
        QuizAttempt.objects.create(student=request.user, quiz=quiz, score_percent=score)
        return render(request, 'quizzes/result.html', {'quiz': quiz, 'score': score, 'correct': correct, 'total': total})

    return render(request, 'quizzes/take_quiz.html', {'quiz': quiz})
