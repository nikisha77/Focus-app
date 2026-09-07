from django.db import models


class Task(models.Model):
    text = models.CharField(max_length=200)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.text


class SessionStats(models.Model):
    completed_sessions = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.completed_sessions} sessions completed"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj