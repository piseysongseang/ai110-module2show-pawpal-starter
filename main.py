from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    TaskType, Priority, Frequency, Preference
)

# --- Tasks for Buddy (dog) ---
morning_walk = Task(
    name="Morning Walk",
    type=TaskType.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    is_required=True,
)

feeding_dog = Task(
    name="Breakfast Feeding",
    type=TaskType.FEEDING,
    duration_minutes=10,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    is_required=True,
)

grooming = Task(
    name="Brush Coat",
    type=TaskType.GROOMING,
    duration_minutes=15,
    priority=Priority.LOW,
    frequency=Frequency.WEEKLY,
)

# --- Tasks for Whiskers (cat) ---
feeding_cat = Task(
    name="Cat Feeding",
    type=TaskType.FEEDING,
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    is_required=True,
)

medication = Task(
    name="Flea Medication",
    type=TaskType.MEDICATION,
    duration_minutes=10,
    priority=Priority.MEDIUM,
    frequency=Frequency.WEEKLY,
    is_required=True,
)

enrichment = Task(
    name="Playtime",
    type=TaskType.ENRICHMENT,
    duration_minutes=20,
    priority=Priority.MEDIUM,
    frequency=Frequency.DAILY,
)

# --- Pets ---
buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
buddy.add_task(morning_walk)
buddy.add_task(feeding_dog)
buddy.add_task(grooming)

whiskers = Pet(name="Whiskers", species="Cat", breed="Siamese", age=5)
whiskers.add_task(feeding_cat)
whiskers.add_task(medication)
whiskers.add_task(enrichment)

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
plan = scheduler.generate_plan()
print(f"Today's Schedule:\n{plan.summarize()}")
