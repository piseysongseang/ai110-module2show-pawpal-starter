# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- The initial UML diagram models a pet care scheduling app with three layers: Data such as TaskType and Priority are enums categorize and rank tasks, Domain like Owner, Pet and Task represent the real-world entities and Planning- Scheduler takses an owner and pet, and outputs a DailyPlan of timed ScheduledTask.
- Classes and their responsibilities:
  - TaskType: labels what kind of care a task is (Walk, Feeding, Medication, others.)
  - Priority: ranks urgency as High(3), Medium(2), or Low(1)
  - Task: the fundamental unit of the system and represents one care activity with a name, type, duration, priority, and an optional notes field. Each task gets a unique auto-generated id.
  - Pet: belongs to an owner and holds a list of Task objects. Supporting adding tasks and removing tasks.
  - Owner: holds the pet(s) and the key scheduling constraint:available_minutes per day. Also stores preferences that influence planning.
  - Scheduler: the planning engine. Takes an Owner and a Pet, then produces a DailyPlan by filtering tasks against the owner's time constraint and sorting them by priority.
  - DailyPlan: the output of the scheduler and contains two lists: tasks that were schedules and tasks that were skipped.
  - ScheduledTask: a thin wrapper that pairs a Task with a concrete start_time and end_time once it has been placed into the plan.

**b. Design changes**

- During implementation, Preferences class is added so that the clients can choose an option instead of typing. Since one owner can have many pets, Shceduler class has changed from pet:Pet to pets:list[Pet].

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
