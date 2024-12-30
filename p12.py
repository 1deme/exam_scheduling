import json
from ortools.sat.python import cp_model
from collections import defaultdict, deque


class Exam:
    def __init__(self, name, registered_students, prerequisites=None):
        self.name = name
        self.registered_students = registered_students
        self.prerequisites = prerequisites if prerequisites else []

class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

class Student:
    def __init__(self, name, exams):
        self.name = name
        self.exams = exams

def create_data_model():
    # Read and parse exams.json
    with open("exams.json", "r") as file:
        exams_data = json.load(file)
    exams = [
        Exam(
            exam["name"], 
            exam["registered_students"], 
            exam.get("prerequisites", [])
        ) 
        for exam in exams_data
    ]


    # Read and parse rooms.json
    with open("rooms.json", "r") as file:
        rooms_data = json.load(file)
    rooms = [Room(room["name"], room["capacity"]) for room in rooms_data]

    # Read and parse students.json
    with open("students.json", "r") as file:
        students_data = json.load(file)
    students = [
        Student(
            student["name"], 
            [exam for exam in exams if exam.name in student["exams"]]
        ) 
        for student in students_data
    ]

    return exams, rooms, students

def main():
    exams, rooms, students = create_data_model()


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

    # Student availability: student_availability[student][slot] = 1 if student is available at slot
    student_availability = {}
    for student in students:
        for slot in range(num_slots):
            student_availability[(student, slot)] = model.NewBoolVar(
                f"student_{student.name}_slot_{slot}")
            


    # Constraints
    # 1. Each exam must be assigned to at least one room in one slot
    for exam in exams:
        model.Add(sum(exam_assignments[(exam, room, slot)] for room in rooms for slot in range(num_slots)) >= 1)

    # 2. Room capacity constraint
    for exam in exams:
        model.Add(
            sum(exam_assignments[(exam, room, slot)] * room.capacity for room in rooms for slot in range(num_slots))
            >= exam.registered_students
        )

    # 3. Student cannot have two exams at the same time
    for student in students:
        for slot in range(num_slots):
            model.Add(
                sum(
                    exam_assignments[(exam, room, slot)]
                    for exam in student.exams
                    for room in rooms
                )
                <= 1
            )

    # 4. Room cannot have two different exams at the same time
    for room in rooms:
        for slot in range(num_slots):
            model.Add(
                sum(
                    exam_assignments[(exam, room, slot)]
                    for exam in exams
                )
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
