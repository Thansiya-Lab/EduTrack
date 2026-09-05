from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Course, Enrollment, Module, VideoProgress
from .utils import get_module_lock_status
from exams.models import ExamResult
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def home(request):
    categories = Category.objects.prefetch_related('courses').all()

    total_courses = Course.objects.filter(is_published=True).count()
    total_students = Enrollment.objects.values('student').distinct().count()
    total_certified = ExamResult.objects.filter(passed=True).values('student').distinct().count()

    return render(request, 'courses/home.html', {
        'categories': categories,
        'total_courses': total_courses,
        'total_students': total_students,
        'total_certified': total_certified,
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    is_enrolled = False
    module_data = []
    all_cleared = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    if is_enrolled:
        module_data, all_cleared = get_module_lock_status(request.user, course)

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'module_data': module_data,
        'all_cleared': all_cleared,
    })


@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    messages.success(request, f"You have enrolled in {course.title}!")
    return redirect('course_detail', slug=course.slug)


@login_required
@require_POST
def mark_video_watched(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    is_enrolled = Enrollment.objects.filter(student=request.user, course=module.course).exists()
    if not is_enrolled:
        return JsonResponse({'ok': False, 'error': 'not enrolled'}, status=403)

    VideoProgress.objects.update_or_create(
        student=request.user, module=module,
        defaults={'completed': True}
    )
    return JsonResponse({'ok': True})
