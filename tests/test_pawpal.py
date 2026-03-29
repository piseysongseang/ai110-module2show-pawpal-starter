from datetime import date, time, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, TaskType, Priority, Frequency


def test_task_completion():
    task = Task(
        name="Morning Walk",
        type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
    )
    assert task.is_completed is False
    task.complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    assert len(pet.tasks) == 0

    task = Task(
        name="Feeding",
        type=TaskType.FEEDING,
        duration_minutes=10,
        priority=Priority.HIGH,
    )
    pet.add_task(task)
    assert len(pet.tasks) == 1


def test_sort_by_time_returns_chronological_order():
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)

    evening = Task(name="Evening Walk", type=TaskType.WALK,
                   duration_minutes=20, priority=Priority.LOW,
                   preferred_time=time(18, 0))
    morning = Task(name="Morning Walk", type=TaskType.WALK,
                   duration_minutes=30, priority=Priority.HIGH,
                   preferred_time=time(7, 0))
    midday = Task(name="Midday Feeding", type=TaskType.FEEDING,
                  duration_minutes=10, priority=Priority.MEDIUM,
                  preferred_time=time(12, 0))
    no_time = Task(name="Playtime", type=TaskType.ENRICHMENT,
                   duration_minutes=15, priority=Priority.LOW)

    for t in [evening, morning, midday, no_time]:
        pet.add_task(t)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(scheduler.pending_tasks)

    timed = [t for t in sorted_tasks if t.preferred_time is not None]
    assert timed[0].preferred_time == time(7, 0)
    assert timed[1].preferred_time == time(12, 0)
    assert timed[2].preferred_time == time(18, 0)
    # untimed task must come last
    assert sorted_tasks[-1].preferred_time is None


def test_daily_task_recurrence_creates_next_day_task():
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)

    walk = Task(name="Morning Walk", type=TaskType.WALK,
                duration_minutes=30, priority=Priority.HIGH,
                frequency=Frequency.DAILY, due_date=date.today())
    pet.add_task(walk)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    new_task = scheduler.complete_task(walk.id)

    assert new_task is not None
    assert new_task.due_date == date.today() + timedelta(days=1)
    assert new_task.is_completed is False
    assert new_task.id != walk.id


def test_conflict_detection_flags_overlapping_times():
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)

    walk = Task(name="Morning Walk", type=TaskType.WALK,
                duration_minutes=30, priority=Priority.HIGH,
                preferred_time=time(7, 0))   # 7:00 – 7:30
    feeding = Task(name="Breakfast", type=TaskType.FEEDING,
                   duration_minutes=10, priority=Priority.HIGH,
                   preferred_time=time(7, 15))  # 7:15 – 7:25  (overlaps)

    pet.add_task(walk)
    pet.add_task(feeding)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) >= 1
    assert any("Morning Walk" in w and "Breakfast" in w for w in warnings)