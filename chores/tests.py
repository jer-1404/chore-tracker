from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Chore, ChoreOccurrence, Member, RotationSlot


def make_household(cadence_days=7, names=("Ana", "Ben", "Cleo")):
    """A chore with a rotation over ``names``, in that order."""
    chore = Chore.objects.create(name="Dishes", cadence_days=cadence_days)
    members = [Member.objects.create(name=name) for name in names]
    for position, member in enumerate(members):
        RotationSlot.objects.create(chore=chore, member=member, position=position)
    return chore, members


class RotationTests(TestCase):
    def test_next_member_follows_rotation_order(self):
        chore, (ana, ben, _) = make_household()

        self.assertEqual(chore.next_member_after(ana), ben)

    def test_next_member_wraps_at_end_of_rotation(self):
        chore, (ana, _, cleo) = make_household()

        self.assertEqual(chore.next_member_after(cleo), ana)

    def test_next_member_is_none_without_a_rotation(self):
        chore = Chore.objects.create(name="Windows")
        member = Member.objects.create(name="Ana")

        self.assertIsNone(chore.next_member_after(member))

    def test_member_outside_rotation_starts_from_the_top(self):
        chore, (ana, _, _) = make_household()
        guest = Member.objects.create(name="Guest")

        self.assertEqual(chore.next_member_after(guest), ana)

    def test_start_rotation_assigns_position_zero(self):
        chore, (ana, _, _) = make_household()

        occurrence = chore.start_rotation()

        self.assertEqual(occurrence.assigned_to, ana)
        self.assertEqual(occurrence.due_on, timezone.localdate())

    def test_start_rotation_does_not_duplicate_an_open_occurrence(self):
        chore, _ = make_household()
        chore.start_rotation()

        self.assertIsNone(chore.start_rotation())
        self.assertEqual(chore.occurrences.count(), 1)


class CompletionTests(TestCase):
    def test_completing_schedules_the_next_member(self):
        chore, (ana, ben, _) = make_household()
        occurrence = chore.start_rotation()

        following = occurrence.complete()

        occurrence.refresh_from_db()
        self.assertIsNotNone(occurrence.completed_at)
        self.assertEqual(following.assigned_to, ben)
        self.assertTrue(following.is_open)

    def test_next_due_date_is_today_plus_cadence(self):
        chore, _ = make_household(cadence_days=3)
        occurrence = chore.start_rotation()

        following = occurrence.complete()

        self.assertEqual(
            following.due_on, timezone.localdate() + timedelta(days=3)
        )

    def test_completing_twice_does_not_skip_a_turn(self):
        chore, _ = make_household()
        occurrence = chore.start_rotation()
        occurrence.complete()

        self.assertIsNone(occurrence.complete())
        self.assertEqual(chore.occurrences.count(), 2)

    def test_a_full_cycle_returns_to_the_first_member(self):
        chore, (ana, _, _) = make_household()
        occurrence = chore.start_rotation()

        for _ in range(3):
            occurrence = occurrence.complete()

        self.assertEqual(occurrence.assigned_to, ana)

    def test_completing_without_a_rotation_creates_nothing(self):
        chore = Chore.objects.create(name="Windows")
        member = Member.objects.create(name="Ana")
        occurrence = ChoreOccurrence.objects.create(
            chore=chore, assigned_to=member, due_on=timezone.localdate()
        )

        self.assertIsNone(occurrence.complete())
        self.assertEqual(chore.occurrences.count(), 1)


class DashboardTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()
        self.chore, (self.ana, _, _) = make_household()

    def occurrence_on(self, due_on):
        return ChoreOccurrence.objects.create(
            chore=self.chore, assigned_to=self.ana, due_on=due_on
        )

    def test_yesterday_is_overdue(self):
        occurrence = self.occurrence_on(self.today - timedelta(days=1))

        response = self.client.get(reverse("dashboard"))

        self.assertIn(occurrence, response.context["overdue"])
        self.assertNotIn(occurrence, response.context["due_today"])

    def test_today_is_due_today(self):
        occurrence = self.occurrence_on(self.today)

        response = self.client.get(reverse("dashboard"))

        self.assertIn(occurrence, response.context["due_today"])
        self.assertNotIn(occurrence, response.context["overdue"])

    def test_tomorrow_is_upcoming(self):
        occurrence = self.occurrence_on(self.today + timedelta(days=1))

        response = self.client.get(reverse("dashboard"))

        self.assertIn(occurrence, response.context["upcoming"])
        self.assertNotIn(occurrence, response.context["due_today"])

    def test_completed_occurrences_are_hidden(self):
        occurrence = self.occurrence_on(self.today)
        occurrence.complete()

        response = self.client.get(reverse("dashboard"))

        self.assertNotIn(occurrence, response.context["due_today"])

    def test_done_button_completes_and_redirects(self):
        occurrence = self.occurrence_on(self.today)

        response = self.client.post(
            reverse("complete_occurrence", args=[occurrence.id])
        )

        self.assertRedirects(response, reverse("dashboard"))
        occurrence.refresh_from_db()
        self.assertIsNotNone(occurrence.completed_at)

    def test_dashboard_rejects_get_on_the_complete_endpoint(self):
        occurrence = self.occurrence_on(self.today)

        response = self.client.get(
            reverse("complete_occurrence", args=[occurrence.id])
        )

        self.assertEqual(response.status_code, 405)
