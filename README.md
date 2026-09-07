# Chore Tracker

A small Django app for managing shared household chores by **rotation**: each
chore has a cadence and an ordered list of housemates, and the app derives whose
turn it is. Built for [AI Dev Tools Zoomcamp 2026](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp),
Module 1 homework.

## What it does

- Keep a list of household members
- Keep a catalog of chores, each with a cadence in days
- Give each chore a rotation order over the members
- See one dashboard of overdue / due today / upcoming chores, and mark them done

Marking a chore done advances the rotation and schedules the next occurrence.

See [`_docs/plan.md`](_docs/plan.md) for the full spec and
[`backlog.md`](backlog.md) for the task breakdown.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Then open http://127.0.0.1:8000/.

## Tests

```bash
uv run python manage.py test
```

## Built with

Spec-driven workflow with a coding agent (Claude Code): vague idea → spec →
backlog → one task at a time → tests.
