import re
from quizzes.models import QuizAttempt
from .models import VideoProgress


def get_youtube_embed_url(url):
    if not url:
        return None
    match = re.search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{11})', url)
    if match:
        return f"https://www.youtube.com/embed/{match.group(1)}?enablejsapi=1&rel=0"
    return None


def get_module_lock_status(user, course):
    """
    Returns (module_data, all_cleared)
    module_data: list of dicts with module, unlocked, video_watched, quiz_accessible, youtube_embed_url
    all_cleared: True only if every module's quiz (if it has one) has been passed
    """
    module_data = []
    previous_passed = True
    all_cleared = True

    modules = list(course.modules.all())
    if not modules:
        all_cleared = False

    for module in modules:
        unlocked = previous_passed
        passed_this_module = False

        video_watched = True
        if module.has_video():
            video_watched = VideoProgress.objects.filter(
                student=user, module=module, completed=True
            ).exists()

        quiz_accessible = unlocked and video_watched

        if hasattr(module, 'quiz'):
            best_attempt = QuizAttempt.objects.filter(
                student=user, quiz=module.quiz
            ).order_by('-score_percent').first()
            if best_attempt and best_attempt.score_percent >= module.quiz.pass_percentage:
                passed_this_module = True
        else:
            passed_this_module = True

        module_data.append({
            'module': module,
            'unlocked': unlocked,
            'video_watched': video_watched,
            'quiz_accessible': quiz_accessible,
            'youtube_embed_url': get_youtube_embed_url(module.video_url) if module.video_url else None,
        })

        if not passed_this_module:
            all_cleared = False

        previous_passed = passed_this_module

    return module_data, all_cleared
