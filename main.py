from datetime import time
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    TaskType, Priority, Frequency, Preference
)

# --- Tasks for Buddy (dog) --- added out of order intentionally ---
grooming = Task(
    name="Brush Coat",
    type=TaskType.GROOMING,
    duration_minutes=15,
    priority=Priority.LOW,
    frequency=Frequency.WEEKLY,
    preferred_time=time(17, 0),   # 5:00 PM
)

morning_walk = Task(
    name="Morning Walk",
    type=TaskType.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    is_required=True,
    preferred_time=time(7, 0),    # 7:00 AM
)

feeding_dog = Task(
    name="Breakfast Feeding",
    type=TaskType.FEEDING,
    duration_minutes=10,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    is_required=True,
    preferred_time=time(8, 0),    # 8:00 AM
)

# --- Tasks for Whiskers (cat) --- added out of order intentionally ---
enrichment = Task(
    name="Playtime",
    type=TaskType.ENRICHMENT,
    duration_minutes=20,
    priority=Priority.MEDIUM,
    frequency=Frequency.DAILY,
)

medication = Task(
    name="Flea Medication",
    type=TaskType.MEDICATION,
    duration_minutes=10,
    priority=Priority.MEDIUM,
    frequency=Frequency.WEEKLY,
    is_required=True,
    preferred_time=time(9, 0),    # 9:00 AM
)

feeding_cat = Task(
    name="Cat Feeding",
    type=TaskType.FEEDING,
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    is_required=True,
    preferred_time=time(7, 30),   # 7:30 AM — overlaps with morning_walk (7:00–7:30)
)

# Intentional conflict: grooming starts at 8:00 AM, same window as feeding_dog (8:00–8:10)
buddy_grooming_conflict = Task(
    name="Quick Brush",
    type=TaskType.GROOMING,
    duration_minutes=20,
    priority=Priority.LOW,
    frequency=Frequency.DAILY,
    preferred_time=time(8, 0),    # 8:00 AM — overlaps with feeding_dog (8:00–8:10)
)

# --- Pets ---
buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
buddy.add_task(grooming)                 # LOW priority, added first
buddy.add_task(morning_walk)             # HIGH priority, added second
buddy.add_task(feeding_dog)              # HIGH priority, added third
buddy.add_task(buddy_grooming_conflict)  # deliberate time conflict with feeding_dog

whiskers = Pet(name="Whiskers", species="Cat", breed="Siamese", age=5)
whiskers.add_task(enrichment)   # MEDIUM, no preferred_time, added first
whiskers.add_task(medication)   # MEDIUM, required, added second
whiskers.add_task(feeding_cat)  # HIGH, required, added third

# --- Owner ---
owner = Owner(
    name="Alex",
    available_minutes=90,
    preferences=[Preference.MORNING_WALKS],
)
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Run Scheduler ---
scheduler = Scheduler(owner)

# Check for conflicts before generating the plan
print("=== Conflict Detection ===")
warnings = scheduler.detect_conflicts()
if warnings:
    for w in warnings:
        print(f"  WARNING: {w}")
else:
    print("  No conflicts detected.")

print()
plan = scheduler.generate_plan()
print(f"=== Today's Schedule ===\n{plan.summarize()}")
