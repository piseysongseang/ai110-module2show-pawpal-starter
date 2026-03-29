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


class Preference(Enum):
    MORNING_WALKS = "morning_walks"
    EVENING_FEEDING = "evening_feeding"
    SKIP_GROOMING = "skip_grooming"
    CLUSTER_TASKS = "cluster_tasks"


@dataclass
class Task:
    name: str
    type: TaskType
    duration_minutes: int
    priority: Priority
    is_required: bool = False
    preferred_time: Optional[time] = None  # e.g. medication must be at 08:00
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __repr__(self) -> str:
        return f"Task({self.name!r}, {self.type.value}, {self.duration_minutes}min, {self.priority.name})"


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, _task: Task) -> None:
        pass

    def remove_task(self, _task_id: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[Preference] = field(default_factory=list)  # structured, not free-text
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, _pet: Pet) -> None:
        pass

    def set_availability(self, _minutes: int) -> None:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: Optional[time] = None
    end_time: Optional[time] = None


@dataclass
class DailyPlan:
    plan_date: date
    owner: Owner                                        # back-reference for context/display
    pet: Pet                                            # back-reference for context/display
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    reasoning: str = ""

    @property
    def total_minutes(self) -> int:                     # computed, never stale
        return sum(st.task.duration_minutes for st in self.scheduled)

    def summarize(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pets: list[Pet]) -> None:
        self.owner = owner
        self.pets = pets                                # supports multiple pets
        # flatten all tasks from all pets into one working list
        self.pending_tasks: list[Task] = [t for pet in pets for t in pet.tasks]

    def generate_plan(self) -> DailyPlan:
        pass

    def filter_by_constraints(self) -> list[Task]:
        pass

    def sort_by_priority(self) -> list[Task]:
        pass

    def reserve_required_tasks(self) -> list[Task]:    # ensures required tasks always make the plan
        pass