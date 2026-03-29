import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, Priority, Frequency


def initialize_session_state():
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name="", available_minutes=60)
    if "pets" not in st.session_state:
        st.session_state.pets = []
    if "plan" not in st.session_state:
        st.session_state.plan = None


initialize_session_state()

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

st.divider()

# --- Owner Setup ---
st.subheader("Owner Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name or "Jordan")
with col2:
    available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=480,
        value=st.session_state.owner.available_minutes
    )

if st.button("Save Owner"):
    st.session_state.owner.name = owner_name
    st.session_state.owner.set_availability(available_minutes)
    st.success(f"Owner '{owner_name}' saved with {available_minutes} min available.")

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
col1, col2, col3, col4 = st.columns(4)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["Dog", "Cat", "Other"])
with col3:
    breed = st.text_input("Breed", value="Mixed")
with col4:
    age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add Pet"):
    new_pet = Pet(name=pet_name, species=species, breed=breed, age=age)
    st.session_state.owner.add_pet(new_pet)
    st.session_state.pets = st.session_state.owner.pets
    st.success(f"Added pet '{pet_name}' to {st.session_state.owner.name or 'owner'}.")

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.table([
        {"Name": p.name, "Species": p.species, "Breed": p.breed, "Age": p.age,
         "Tasks": len(p.tasks)}
        for p in st.session_state.owner.pets
    ])

st.divider()

# --- Add a Task to a Pet ---
st.subheader("Add a Task")

if not st.session_state.owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in st.session_state.owner.pets]
    col1, col2, col3 = st.columns(3)
    with col1:
        target_pet = st.selectbox("Assign to pet", pet_names)
        task_name = st.text_input("Task name", value="Morning walk")
    with col2:
        task_type = st.selectbox("Type", [t.value for t in TaskType])
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", [p.name for p in Priority])
        frequency = st.selectbox("Frequency", [f.value for f in Frequency])
        is_required = st.checkbox("Required?")

    if st.button("Add Task"):
        task = Task(
            name=task_name,
            type=TaskType(task_type),
            duration_minutes=int(duration),
            priority=Priority[priority],
            frequency=Frequency(frequency),
            is_required=is_required,
        )
        pet = next(p for p in st.session_state.owner.pets if p.name == target_pet)
        pet.add_task(task)
        st.success(f"Added task '{task_name}' to {target_pet}.")

    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("All tasks across pets:")
        st.table([
            {"Pet": p.name, "Task": t.name, "Type": t.type.value,
             "Duration": t.duration_minutes, "Priority": t.priority.name,
             "Required": t.is_required}
            for p in st.session_state.owner.pets for t in p.tasks
        ])

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Daily Schedule")

if st.button("Generate Schedule"):
    if not st.session_state.owner.pets:
        st.warning("Add at least one pet with tasks before generating a schedule.")
    elif not st.session_state.owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        st.session_state.plan = scheduler.generate_plan()

if st.session_state.plan:
    plan = st.session_state.plan
    st.success(f"Schedule generated — {plan.total_minutes} min of {st.session_state.owner.available_minutes} min used.")

    if plan.scheduled:
        st.markdown("**Scheduled tasks:**")
        st.table([
            {"Task": s.task.name, "Type": s.task.type.value,
             "Duration": s.task.duration_minutes, "Priority": s.task.priority.name,
             "Required": s.task.is_required}
            for s in plan.scheduled
        ])

    if plan.skipped:
        st.markdown("**Skipped tasks (didn't fit):**")
        st.table([
            {"Task": t.name, "Duration": t.duration_minutes, "Priority": t.priority.name}
            for t in plan.skipped
        ])

    st.markdown(f"**Reasoning:** {plan.reasoning}")