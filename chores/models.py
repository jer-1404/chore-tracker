from datetime import timedelta

from django.db import models
from django.utils import timezone


class Member(models.Model):
    """Someone who lives in the household and takes turns at chores."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Chore(models.Model):
    """A recurring job, with how often it needs doing."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    cadence_days = models.PositiveIntegerField(
        default=7,
        help_text="How many days after being done this chore comes round again.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def rotation_members(self):
        """The members in rotation order."""
        return [slot.member for slot in self.rotation_slots.all()]

    def next_member_after(self, member):
        """The member whose turn follows ``member``, wrapping at the end.

        Returns ``None`` when the chore has no rotation set up. A member who is
        not in the rotation is treated as "start from the top", so removing
        someone from the rotation cannot strand the chore.
        """
        members = self.rotation_members()
        if not members:
            return None
        try:
            index = members.index(member)
        except ValueError:
            return members[0]
        return members[(index + 1) % len(members)]

    def start_rotation(self, due_on=None):
        """Create the first open occurrence, for the member in position 0.

        Does nothing and returns ``None`` if the chore has no rotation or
        already has an open occurrence.
        """
        members = self.rotation_members()
        if not members:
            return None
        if self.occurrences.filter(completed_at__isnull=True).exists():
            return None
        return ChoreOccurrence.objects.create(
            chore=self,
            assigned_to=members[0],
            due_on=due_on or timezone.localdate(),
        )


class RotationSlot(models.Model):
    """One position in a chore's rotation order."""

    chore = models.ForeignKey(
        Chore, on_delete=models.CASCADE, related_name="rotation_slots"
    )
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="rotation_slots"
    )
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["chore", "position"], name="unique_position_per_chore"
            )
        ]

    def __str__(self):
        return f"{self.chore} #{self.position}: {self.member}"


class ChoreOccurrence(models.Model):
    """One turn at a chore: who owes it, when it is due, whether it is done."""

    chore = models.ForeignKey(
        Chore, on_delete=models.CASCADE, related_name="occurrences"
    )
    assigned_to = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="occurrences"
    )
    due_on = models.DateField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["due_on", "chore__name"]

    def __str__(self):
        state = "done" if self.completed_at else f"due {self.due_on}"
        return f"{self.chore} — {self.assigned_to} ({state})"

    @property
    def is_open(self):
        return self.completed_at is None

    def complete(self):
        """Mark this turn done and schedule the next one.

        Returns the newly created occurrence, or ``None`` if the chore has no
        rotation to advance. Completing an already-completed occurrence is a
        no-op so a double-submitted form cannot skip someone's turn.
        """
        if self.completed_at is not None:
            return None

        self.completed_at = timezone.now()
        self.save(update_fields=["completed_at"])

        next_member = self.chore.next_member_after(self.assigned_to)
        if next_member is None:
            return None

        return ChoreOccurrence.objects.create(
            chore=self.chore,
            assigned_to=next_member,
            due_on=timezone.localdate() + timedelta(days=self.chore.cadence_days),
        )
