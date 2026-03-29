from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
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
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def reset(self) -> None:
        """Reset this task to incomplete for the next scheduling cycle."""
        self.is_completed = False

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
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        self.pets = [p for p in self.pets if p.name != pet_name]

    def set_availability(self, minutes: int) -> None:
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
        return sum(st.task.duration_minutes for st in self.scheduled)

    def summarize(self) -> str:
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
        self.owner = owner
        self.pending_tasks: list[Task] = owner.get_all_pending_tasks()

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

    def reserve_required_tasks(self) -> list[Task]:
        """Return all required tasks — these always make the plan regardless of time."""
        return [t for t in self.pending_tasks if t.is_required]