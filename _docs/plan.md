# Chore Tracker — Product Plan

## The idea we started from

> A tool for managing shared household chores

## Who it is for

A small household (2–6 people) sharing a flat or house, where the recurring
argument is not *what* needs doing but *whose turn it is*. Everyone already
knows the bathroom needs cleaning; nobody agrees on who cleaned it last.

## The problem we are solving

Shared-chore friction comes from three gaps:

1. **No memory.** Nobody remembers who did the dishes on Tuesday.
2. **No fairness.** The same person quietly absorbs the unpleasant chores.
3. **No visibility.** You only find out a chore was skipped when it smells.

Chore Tracker fixes these by making the *rotation* the source of truth: each
chore has a fixed cadence and a fixed order of people, and the app derives whose
turn it is instead of asking anyone to negotiate it.

## Scope

### In scope (v1)

Four features, in build order:

1. **Household members**
   A household has named members. Members are created and listed in the app; no
   authentication, no invites, no email. This is a wall-mounted tablet app, not
   a social network.

2. **Chore catalog with cadence**
   Each chore has a name, an optional description, and a cadence in days
   (e.g. dishes = 1, bathroom = 7, windows = 30). The cadence is what makes a
   chore recurring rather than a one-off to-do.

3. **Rotation assignment**
   Each chore holds an ordered list of members. When an occurrence of a chore is
   completed, the next occurrence is assigned to the next member in the rotation
   and scheduled `cadence` days out. The rotation is the fairness mechanism — it
   is deterministic and visible, so nobody has to argue about it.

4. **Due / overdue dashboard**
   One screen listing every open chore occurrence, grouped as *overdue*, *due
   today*, and *upcoming*, each showing who owns it. A single "mark done" action
   completes an occurrence and rolls the rotation forward.

### Out of scope (v1)

Deliberately excluded so v1 stays finishable:

- User accounts, passwords, permissions — anyone with the URL is trusted.
- Push notifications, email, or SMS reminders.
- Points, streaks, leaderboards, or any gamification.
- Multiple households in one deployment.
- Swapping or trading turns — you do your turn or you mark it done late.
- Mobile app; a responsive web page is enough.

## Data model sketch

- `Member` — `name`
- `Chore` — `name`, `description`, `cadence_days`
- `RotationSlot` — `chore` → `member`, `position` (ordered rotation per chore)
- `ChoreOccurrence` — `chore`, `assigned_to`, `due_on`, `completed_at`

`ChoreOccurrence` is the only table that changes day to day; the first three are
configuration.

## Key decisions

| Decision | Why |
|---|---|
| Rotation is derived, not manual | Removes the negotiation that causes the argument in the first place. |
| Cadence in days, not cron | A household thinks "every 3 days", not `0 0 */3 * *`. |
| Occurrences are generated on completion, not by a scheduler | No background worker, no cron. The app stays a single Django process. |
| No auth in v1 | The threat model of a shared kitchen tablet does not include attackers. |

## What "done" looks like for v1

- Members and chores can be created, and a chore can be given a rotation.
- The dashboard shows open occurrences split into overdue / today / upcoming.
- Marking an occurrence done advances the rotation and schedules the next one.
- Tests cover rotation advancement, due-date arithmetic, and the dashboard
  grouping — the three places where the logic can actually be wrong.
