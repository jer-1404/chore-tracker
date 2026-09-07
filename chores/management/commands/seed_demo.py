from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from chores.models import Chore, ChoreOccurrence, Member, RotationSlot

HOUSEHOLD = ["Ana", "Ben", "Cleo"]

CHORES = [
    ("Dishes", "Empty the drying rack and run the dishwasher.", 1),
    ("Bathroom", "Sink, toilet, shower, mirror.", 7),
    ("Take out recycling", "Blue bin goes out Tuesday night.", 14),
    ("Windows", "Inside only.", 30),
]


class Command(BaseCommand):
    help = "Create a sample household so the dashboard is not empty."

    def handle(self, *args, **options):
        if Member.objects.exists():
            self.stdout.write(self.style.WARNING("Household already set up; nothing to do."))
            return

        members = [Member.objects.create(name=name) for name in HOUSEHOLD]
        today = timezone.localdate()

        for offset, (name, description, cadence) in enumerate(CHORES):
            chore = Chore.objects.create(
                name=name, description=description, cadence_days=cadence
            )
            for position, member in enumerate(members):
                RotationSlot.objects.create(
                    chore=chore, member=member, position=position
                )
            # Stagger the first due dates so the dashboard shows all three groups.
            ChoreOccurrence.objects.create(
                chore=chore,
                assigned_to=members[offset % len(members)],
                due_on=today + timedelta(days=offset - 1),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(members)} members and {len(CHORES)} chores."
            )
        )
