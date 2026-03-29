from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import Enum
from typing import Optional
import uuid


class TaskType(Enum):
    WALK = "Walk"
    FEEDING = "Feeding"
    MEDICATION = "Medication"
    ENRICHMENT = "Enrichment"
    GROOMING = "Grooming"
    VET = "Vet"
    OTHER = "Other"


class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


class Preference(Enum):
    MORNING_WALKS = "morning_walks"
    EVENING_FEEDING = "evening_feeding"
    SKIP_GROOMING = "skip_grooming"
    CLUSTER_TASKS = "cluster_tasks"


@dataclass
class Task:
    """Represents a single pet care activity."""
    name: str
    type: TaskType
    duration_minutes: int
    priority: Priority
    frequency: Frequency = Frequency.DAILY
    is_required: bool = False
    is_completed: bool = False
    preferred_time: Optional[time] = None
    due_date: date = field(default_factory=date.today)
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def reset(self) -> None:
        """Reset this task to incomplete for the next scheduling cycle."""
        self.is_completed = False

    def next_occurrence(self) -> Optional[Task]:
        """Return a fresh copy of this task for its next occurrence, or None if AS_NEEDED."""
        if self.frequency == Frequency.AS_NEEDED:
            return None
        delta = timedelta(days=1) if self.frequency == Frequency.DAILY else timedelta(weeks=1)
        return Task(
            name=self.name,
            type=self.type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            is_required=self.is_required,
            is_completed=False,
            preferred_time=self.preferred_time,
            due_date=self.due_date + delta,
            notes=self.notes,
        )

    def __repr__(self) -> str:
        status = "done" if self.is_completed else "pending"
        return f"Task({self.name!r}, {self.type.value}, {self.duration_minutes}min, {self.priority.name}, {status})"


@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks."""
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet's list by its unique ID."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.is_completed]
    
    def get_tasks_due_today(self) -> list[Task]:
        """Return all incomplete tasks due today."""
        today = date.today()
        return [t for t in self.tasks if t.due_date == today and not t.is_completed]

    def __repr__(self) -> str:
        return f"Pet({self.name!r}, {self.species}, {len(self.tasks)} tasks)"


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    name: str
    available_minutes: int
    preferences: list[Preference] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from this owner's list by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def set_availability(self, minutes: int) -> None:
        """Update the number of minutes the owner has available today."""
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[Task]:
        """Returns every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list[Task]:
        """Returns only incomplete tasks across all pets."""
        return [task for pet in self.pets for task in pet.get_pending_tasks()]

    def __repr__(self) -> str:
        return f"Owner({self.name!r}, {len(self.pets)} pets, {self.available_minutes}min/day)"


@dataclass
class ScheduledTask:
    """A Task placed at a specific time in the day."""
    task: Task
    start_time: Optional[time] = None
    end_time: Optional[time] = None


@dataclass
class DailyPlan:
    """The output of the Scheduler for a given day."""
    plan_date: date
    owner: Owner
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    reasoning: str = ""

    @property
    def total_minutes(self) -> int:
        """Compute total scheduled time in minutes from the scheduled task list."""
        return sum(st.task.duration_minutes for st in self.scheduled)

    def summarize(self) -> str:
        """Return a human-readable summary of the day's scheduled and skipped tasks."""
        lines = [
            f"Plan for {self.owner.name} — {self.plan_date}",
            f"Scheduled: {len(self.scheduled)} tasks ({self.total_minutes} min)",
            f"Skipped:   {len(self.skipped)} tasks",
        ]
        for st in self.scheduled:
            time_str = f"{st.start_time} → {st.end_time}" if st.start_time else "unscheduled"
            lines.append(f"  • {st.task.name} [{time_str}]")
        if self.skipped:
            lines.append("Skipped:")
            for t in self.skipped:
                lines.append(f"  • {t.name} ({t.priority.name})")
        if self.reasoning:
            lines.append(f"Reasoning: {self.reasoning}")
        return "\n".join(lines)


class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with an owner and flatten all pending tasks from their pets."""
        self.owner = owner
        self.pending_tasks: list[Task] = owner.get_all_pending_tasks()

    def detect_conflicts(self) -> list[str]:
        """Check for scheduling problems and return a list of warning messages.

        Returns an empty list if no conflicts are found. Never raises.
        """
        warnings: list[str] = []

        # 1. Required tasks alone exceed available time
        required = self.reserve_required_tasks()
        required_minutes = sum(t.duration_minutes for t in required)
        if required_minutes > self.owner.available_minutes:
            warnings.append(
                f"Required tasks total {required_minutes} min but owner only has "
                f"{self.owner.available_minutes} min available. Some required tasks will be tight."
            )

        # 2. Duplicate task names within the same pet
        for pet in self.owner.pets:
            seen: set[str] = set()
            for task in pet.tasks:
                if task.name in seen:
                    warnings.append(
                        f"Pet '{pet.name}' has duplicate task name: '{task.name}'."
                    )
                seen.add(task.name)

        # 3. Overlapping preferred_times (two tasks whose windows collide)
        timed = [t for t in self.pending_tasks if t.preferred_time is not None]
        for i, a in enumerate(timed):
            a_start = a.preferred_time.hour * 60 + a.preferred_time.minute
            a_end = a_start + a.duration_minutes
            for b in timed[i + 1:]:
                b_start = b.preferred_time.hour * 60 + b.preferred_time.minute
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Time conflict: '{a.name}' ({a.preferred_time}) and "
                        f"'{b.name}' ({b.preferred_time}) overlap."
                    )

        # 4. A single task is longer than the entire available window
        for task in self.pending_tasks:
            if task.duration_minutes > self.owner.available_minutes:
                warnings.append(
                    f"Task '{task.name}' ({task.duration_minutes} min) exceeds the owner's "
                    f"entire available time ({self.owner.available_minutes} min) and can never be scheduled."
                )

        return warnings

    def generate_plan(self) -> DailyPlan:
        """Build a DailyPlan that fits within the owner's available time."""
        required = self.reserve_required_tasks()
        optional = self.sort_by_priority()

        scheduled: list[ScheduledTask] = []
        skipped: list[Task] = []
        minutes_used = sum(t.duration_minutes for t in required)

        # Always include required tasks
        for task in required:
            scheduled.append(ScheduledTask(task=task))

        # Fill remaining time with optional tasks by priority
        for task in optional:
            if minutes_used + task.duration_minutes <= self.owner.available_minutes:
                scheduled.append(ScheduledTask(task=task))
                minutes_used += task.duration_minutes
            else:
                skipped.append(task)

        reasoning = (
            f"Reserved {len(required)} required task(s). "
            f"Fit {len(scheduled) - len(required)} optional task(s) "
            f"within {self.owner.available_minutes} min limit. "
            f"Skipped {len(skipped)} task(s) due to time constraints."
        )

        return DailyPlan(
            plan_date=date.today(),
            owner=self.owner,
            scheduled=scheduled,
            skipped=skipped,
            reasoning=reasoning,
        )

    def filter_by_constraints(self) -> list[Task]:
        """Return tasks that individually fit within available time, excluding required ones."""
        return [
            t for t in self.pending_tasks
            if not t.is_required and t.duration_minutes <= self.owner.available_minutes
        ]

    def sort_by_priority(self) -> list[Task]:
        """Return optional tasks sorted by priority (HIGH first) then duration (shortest first)."""
        optional = self.filter_by_constraints()
        return sorted(optional, key=lambda t: (-t.priority.value, t.duration_minutes))

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task complete and automatically queue the next occurrence for recurring tasks.

        Returns the new Task instance if one was created, or None for AS_NEEDED tasks.
        """
        # Find the task in pending_tasks
        task = next((t for t in self.pending_tasks if t.id == task_id), None)
        if task is None:
            return None

        task.complete()

        # Find which pet owns this task and add the next occurrence to it
        next_task = task.next_occurrence()
        if next_task is not None:
            for pet in self.owner.pets:
                if any(t.id == task_id for t in pet.tasks):
                    pet.add_task(next_task)
                    self.pending_tasks.append(next_task)
                    break

        return next_task

    def reserve_required_tasks(self) -> list[Task]:
        """Return all required tasks — these always make the plan regardless of time."""
        return [t for t in self.pending_tasks if t.is_required]

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """Filter pending_tasks by completion status, pet name, or both.

        Args:
            completed: If True, return only completed tasks. If False, only incomplete.
                       If None, completion status is not filtered.
            pet_name:  If provided, return only tasks belonging to that pet.
                       If None, tasks from all pets are included.
        """
        pet_task_ids: Optional[set[str]] = None
        if pet_name is not None:
            matched = next((p for p in self.owner.pets if p.name == pet_name), None)
            pet_task_ids = {t.id for t in matched.tasks} if matched else set()

        results: list[Task] = []
        for task in self.pending_tasks:
            if completed is not None and task.is_completed != completed:
                continue
            if pet_task_ids is not None and task.id not in pet_task_ids:
                continue
            results.append(task)
        return results

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by preferred_time, placing tasks with no time preference at the end."""
        timed = sorted(
            [t for t in tasks if t.preferred_time is not None],
            key=lambda t: t.preferred_time,
        )
        untimed = [t for t in tasks if t.preferred_time is None]
        return timed + untimed