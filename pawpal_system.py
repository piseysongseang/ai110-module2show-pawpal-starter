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


@dataclass
class Task:
    name: str
    type: TaskType
    duration_minutes: int
    priority: Priority
    is_required: bool = False
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
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def set_availability(self, minutes: int) -> None:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: Optional[time] = None
    end_time: Optional[time] = None


@dataclass
class DailyPlan:
    plan_date: date
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    reasoning: str = ""

    def summarize(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.pending_tasks: list[Task] = []

    def generate_plan(self) -> DailyPlan:
        pass

    def filter_by_constraints(self) -> list[Task]:
        pass

    def sort_by_priority(self) -> list[Task]:
        pass