from pawpal_system import Task, Pet, TaskType, Priority


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