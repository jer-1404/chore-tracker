# Backlog

Derived from [`_docs/plan.md`](_docs/plan.md). Tasks are ordered so that each one
leaves the app runnable and each one is small enough to hand to an agent alone.

## Task 1 — Member and Chore models with admin

Create the `Member` model (`name`) and the `Chore` model (`name`,
`description`, `cadence_days`). Register both in the Django admin so a
household can be set up without any custom UI yet. Add the migration.

**Done when:** `manage.py migrate` succeeds and both models are editable at
`/admin/`.

## Task 2 — Rotation model

Add `RotationSlot` (`chore`, `member`, `position`) with a uniqueness constraint
on `(chore, position)`, plus a `Chore.next_member_after(member)` helper that
returns the next member in the rotation and wraps around at the end. Register it
as an inline on `Chore` in the admin.

**Done when:** a chore can be given an ordered rotation, and
`next_member_after` wraps from the last slot back to the first.

## Task 3 — ChoreOccurrence and completion logic

Add `ChoreOccurrence` (`chore`, `assigned_to`, `due_on`, `completed_at`) and a
`complete()` method that stamps `completed_at`, then creates the next open
occurrence assigned to the next member in the rotation and due
`cadence_days` from today. Add `Chore.start_rotation()` to create the first
occurrence for the member in position 0.

**Done when:** completing an occurrence produces exactly one new open occurrence
with the next member and the correct due date.

## Task 4 — Dashboard view

Add a single view at `/` that lists all open occurrences grouped into
**overdue** (`due_on < today`), **due today**, and **upcoming**, each showing the
chore name and assignee. Wire it into `config/urls.py` with a template.

**Done when:** the three groups render with the right occurrences in each.

## Task 5 — Mark done action

Add a POST endpoint that calls `complete()` on an occurrence and redirects back
to the dashboard, with a "Done" button on each dashboard row.

**Done when:** clicking Done removes the row and the next occurrence appears in
the upcoming group.

## Task 6 — Tests

Cover the three places the logic can actually be wrong:

- rotation advancement, including wrap-around at the end of the rotation
- due-date arithmetic on completion (`today + cadence_days`)
- dashboard grouping boundaries (yesterday / today / tomorrow)

**Done when:** `uv run python manage.py test` passes.

## Task 7 — Seed command

Add a `seed_demo` management command that creates a sample household so the app
is not empty on first run.

**Done when:** `manage.py seed_demo` populates members, chores, rotations, and
open occurrences.
