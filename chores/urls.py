from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "occurrences/<int:occurrence_id>/complete/",
        views.complete_occurrence,
        name="complete_occurrence",
    ),
]
