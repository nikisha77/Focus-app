"""Tests for the Focus Flow Django app."""
from django.test import TestCase

from core.models import SessionStats, Task


class TaskModelTests(TestCase):
    def test_create_task_defaults_to_unchecked(self):
        task = Task.objects.create(text="Read a book")
        self.assertFalse(task.done)
        self.assertEqual(task.text, "Read a book")

    def test_str_returns_text(self):
        task = Task.objects.create(text="Hello")
        self.assertEqual(str(task), "Hello")

    def test_ordering_newest_first(self):
        Task.objects.create(text="Old")
        Task.objects.create(text="New")
        self.assertEqual([t.text for t in Task.objects.all()], ["New", "Old"])


class SessionStatsTests(TestCase):
    def test_get_solo_creates_singleton(self):
        SessionStats.objects.all().delete()
        s = SessionStats.get_solo()
        self.assertEqual(s.completed_sessions, 0)

    def test_get_solo_returns_same_row(self):
        SessionStats.objects.all().delete()
        a = SessionStats.get_solo()
        b = SessionStats.get_solo()
        self.assertEqual(a.pk, b.pk)

    def test_increment(self):
        SessionStats.objects.all().delete()
        s = SessionStats.get_solo()
        s.completed_sessions += 1
        s.save()
        self.assertEqual(SessionStats.get_solo().completed_sessions, 1)


class ViewTests(TestCase):
    def test_add_task_returns_json(self):
        response = self.client.post("/tasks/add/", {"text": "Test task"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["text"], "Test task")
        self.assertFalse(data["done"])
        self.assertEqual(Task.objects.count(), 1)

    def test_toggle_task(self):
        task = Task.objects.create(text="X")
        response = self.client.post(
            f"/tasks/{task.id}/toggle/", {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertTrue(task.done)

    def test_toggle_nonexistent_returns_404(self):
        response = self.client.post("/tasks/9999/toggle/", {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_delete_task(self):
        task = Task.objects.create(text="X")
        response = self.client.post(
            f"/tasks/{task.id}/delete/", {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 0)

    def test_session_complete_increments(self):
        SessionStats.objects.all().delete()
        response = self.client.post("/session/complete/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["completed_sessions"], 1)
        self.assertEqual(SessionStats.get_solo().completed_sessions, 1)

    def test_index_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Focus Flow")