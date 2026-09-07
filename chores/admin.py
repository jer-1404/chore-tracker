from django.contrib import admin

from .models import Chore, ChoreOccurrence, Member, RotationSlot


class RotationSlotInline(admin.TabularInline):
    model = RotationSlot
    extra = 1
    ordering = ["position"]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ["name", "cadence_days"]
    inlines = [RotationSlotInline]


@admin.register(ChoreOccurrence)
class ChoreOccurrenceAdmin(admin.ModelAdmin):
    list_display = ["chore", "assigned_to", "due_on", "completed_at"]
    list_filter = ["chore", "assigned_to"]
