from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('quiz/', include('quizzes.urls')),
    path('exam/', include('exams.urls')),
    path('progress/', include('progress_tracker.urls')),
    path('', include('courses.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
admin.site.site_header = "EduTrack Administration"
admin.site.site_title = "EduTrack Admin"
admin.site.index_title = "Welcome to EduTrack Admin Panel"
