from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ChoreOccurrence


def dashboard(request):
    """Every open turn, split into overdue / due today / upcoming."""
    today = timezone.localdate()
    open_occurrences = ChoreOccurrence.objects.filter(
        completed_at__isnull=True
    ).select_related("chore", "assigned_to")

    return render(
        request,
        "chores/dashboard.html",
        {
            "today": today,
            "overdue": open_occurrences.filter(due_on__lt=today),
            "due_today": open_occurrences.filter(due_on=today),
            "upcoming": open_occurrences.filter(due_on__gt=today),
        },
    )


@require_POST
def complete_occurrence(request, occurrence_id):
    occurrence = get_object_or_404(ChoreOccurrence, pk=occurrence_id)
    occurrence.complete()
    return redirect("dashboard")
