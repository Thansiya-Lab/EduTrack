from django.contrib import admin
from .models import Category, Course, Module, Enrollment, VideoProgress


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor_name', 'is_published')
    list_filter = ('category', 'is_published')
    inlines = [ModuleInline]


admin.site.register(Category)
admin.site.register(Enrollment)
admin.site.register(VideoProgress)
