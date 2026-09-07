from django.contrib import admin

from .models import SessionStats, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("text", "done", "created_at")
    list_filter = ("done",)
    search_fields = ("text",)


@admin.register(SessionStats)
class SessionStatsAdmin(admin.ModelAdmin):
    list_display = ("completed_sessions",)