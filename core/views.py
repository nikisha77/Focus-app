import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .models import SessionStats, Task


def _serialize_task(t):
    return {"id": t.id, "text": t.text, "done": t.done}


def index(request):
    tasks = Task.objects.all()
    stats = SessionStats.get_solo()
    return render(request, "core/index.html", {
        "tasks": [_serialize_task(t) for t in tasks],
        "completed_sessions": stats.completed_sessions,
    })


@csrf_protect
@require_http_methods(["POST"])
def add_task(request):
    payload = _parse_payload(request)
    text = (payload.get("text") or "").strip()
    if not text:
        return HttpResponseBadRequest("text required")
    task = Task.objects.create(text=text)
    return JsonResponse(_serialize_task(task))


@csrf_protect
@require_http_methods(["POST"])
def toggle_task(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
        task.done = not task.done
        task.save()
        return JsonResponse(_serialize_task(task))
    except Task.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)


@csrf_protect
@require_http_methods(["POST"])
def delete_task(request, task_id):
    Task.objects.filter(pk=task_id).delete()
    return JsonResponse({"ok": True})


@csrf_protect
@require_http_methods(["POST"])
def session_complete(request):
    stats = SessionStats.get_solo()
    stats.completed_sessions += 1
    stats.save()
    return JsonResponse({"completed_sessions": stats.completed_sessions})


def _parse_payload(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8"))
        except Exception:
            return {}
    return request.POST