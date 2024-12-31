import json
from ortools.sat.python import cp_model

class Course:
    def __init__(self, name, student_emails):
        self.name = name
        self.student_emails = student_emails

class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

def create_data_model():
    with open("exams.json", "r") as file:
        courses_data = json.load(file)
    courses = [
        Course(
            course["name"],
            course["student_emails"]
        ) 
        for course in courses_data
    ]

    with open("rooms.json", "r") as file:
        rooms_data = json.load(file)
    rooms = [Room(room["name"], room["capacity"]) for room in rooms_data]

    return courses, rooms

def main():
    exams, rooms = create_data_model()


    # Create CP-SAT model
    model = cp_model.CpModel()

    num_slots = 20  # Adjust as needed

    # Decision variables: exam_assignments[exam][room][slot] = 1 if exam is assigned to room at slot
    exam_assignments = {}
    for exam in exams:
        for room in rooms:
            for slot in range(num_slots):
                exam_assignments[(exam, room, slot)] = model.NewBoolVar(
                    f"exam_{exam.name}_room_{room.name}_slot_{slot}")

    # Constraints
    # 1. Each exam must be assigned to at least one room in one slot. 100 constraints
    for exam in exams:
        model.Add(sum(exam_assignments[(exam, room, slot)] for room in rooms for slot in range(num_slots)) >= 1)


    # 2. Room capacity constraint. 100 constraints
    for exam in exams:
        model.Add(
            sum(exam_assignments[(exam, room, slot)] * room.capacity for room in rooms for slot in range(num_slots))
            >= len(exam.student_emails)
        )

            
    # 4. only one exam per room per slot. 200 constraints
    for room in rooms:
        for slot in range(num_slots):
            model.Add(
                sum(
                    exam_assignments[(exam, room, slot)]
                    for exam in exams
                ) <= 1
            )

    # 3. Conflict constraint: Exams with common students cannot be scheduled in the same slot
    for i in range(len(exams)):
        for j in range(i + 1, len(exams)):
            exam1 = exams[i]
            exam2 = exams[j]

            # Check if there are common students
            if set(exam1.student_emails) & set(exam2.student_emails):
                # Add constraint for all slots
                for slot in range(num_slots):
                    model.Add(
                        sum(exam_assignments[(exam1, room, slot)] for room in rooms) +
                        sum(exam_assignments[(exam2, room, slot)] for room in rooms)
                        <= 1
                    )

    
    # Decision variable: slot_used[slot] = 1 if any exam is scheduled in that slot
    slot_used = {}
    for slot in range(num_slots):
        slot_used[slot] = model.NewBoolVar(f"slot_used_{slot}")

    # Link slot_used to exam assignments
    for slot in range(num_slots):
        for room in rooms:
            for exam in exams:
                model.Add(slot_used[slot] >= exam_assignments[(exam, room, slot)])

    # Minimize the number of slots used
    model.Minimize(sum(slot_used[slot] for slot in range(num_slots)))
    
    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    solver.parameters.search_branching = cp_model.FIXED_SEARCH


    # Generate the solution and write to JSON
    if status == cp_model.OPTIMAL:
        schedule = {}
        for slot in range(num_slots):
            slot_data = []
            for room in rooms:
                for exam in exams:
                    if solver.Value(exam_assignments[(exam, room, slot)]) == 1:
                        slot_data.append({"room": room.name, "exam": exam.name})
            schedule[f"Slot {slot}"] = slot_data

        # Save to JSON file
        with open("schedule.json", "w") as json_file:
            json.dump(schedule, json_file, indent=4)
        print("Schedule saved to 'schedule.json'")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
