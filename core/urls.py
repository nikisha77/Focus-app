from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tasks/add/", views.add_task, name="add_task"),
    path("tasks/<int:task_id>/toggle/", views.toggle_task, name="toggle_task"),
    path("tasks/<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path("session/complete/", views.session_complete, name="session_complete"),
]