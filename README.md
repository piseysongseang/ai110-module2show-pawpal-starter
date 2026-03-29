# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Smart Scheduling

PawPal+ uses a focused daily scheduling strategy: rather than presenting every task ever created, the scheduler only surfaces tasks that are **due today** and **not yet completed**.

This is powered by `Pet.get_tasks_due_today()`, which filters each pet's task list to those whose `due_date` matches the current date. The result feeds directly into the `Scheduler`, keeping the daily plan short, actionable, and relevant to the owner's actual day.

When a task is marked complete, `Scheduler.complete_task()` automatically calls `Task.next_occurrence()` to calculate and assign the next `due_date` — one day forward for `DAILY` tasks, one week forward for `WEEKLY` tasks. `AS_NEEDED` tasks are never auto-rescheduled and must be re-added manually.

This design makes a deliberate tradeoff: the plan stays focused and avoids overwhelming the owner with future tasks, but it requires the owner to mark tasks complete so the system can keep the schedule accurate going forward.

### Testing PawPal+

Run the full test suite with:

```bash
python -m pytest tests/test_pawpal.py -v
```

**What the tests cover:**

| Test | What it verifies |
|---|---|
| `test_task_completion` | Calling `complete()` sets `is_completed` to `True` |
| `test_add_task_increases_pet_task_count` | `pet.add_task()` correctly appends to the task list |
| `test_sort_by_time_returns_chronological_order` | Tasks with `preferred_time` are ordered earliest-first; untimed tasks go last |
| `test_daily_task_recurrence_creates_next_day_task` | Completing a `DAILY` task generates a new task with `due_date = today + 1 day` and a fresh `id` |
| `test_conflict_detection_flags_overlapping_times` | Overlapping `preferred_time` windows produce a warning message naming both tasks |

**Confidence Level: ★★★☆☆ (3/5)**

The core logic — task completion, recurrence, sorting, and conflict detection — is tested and working. The rating is not higher because:
- Required tasks exceeding the time budget are not yet tested
- `AS_NEEDED` recurrence returning `None` has no test
- `get_tasks_due_today()` past/future date filtering is untested
- The Streamlit UI has no tests at all
- No test covers the full `generate_plan()` output end-to-end
