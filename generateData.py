import json
import random

# Read exams and student emails from the JSON files
with open('exams.json', 'r') as f:
    exams = json.load(f)

with open('studentMails.json', 'r') as f:
    student_emails = json.load(f)

# Create the exam-student assignments
def create_exam_student_assignments(exams, student_emails):
    # Ensure the first 700 students are assigned to the first 55 subjects
    # and the remaining 300 students to the last 25 subjects
    group_1_students = student_emails[:700]  # First 700 students
    group_2_students = student_emails[700:]  # Last 300 students

    # Split the exams into two parts
    group_1_exams = exams[:55]  # First 55 subjects
    group_2_exams = exams[55:]  # Remaining 25 subjects

    # Result to store the final exam assignments
    exam_student_assignments = []

    # Function to assign students to exams
    def assign_students_to_exams(exams_list, students_list):
        random.shuffle(students_list)  # Shuffle students for randomness
        assignments = []
        
        # Assign each exam to a random selection of students
        for exam in exams_list:
            # Random number of students for the current exam, between 10 and 400
            num_students = random.randint(10, 400)
            assigned_students = students_list[:num_students]
            students_list = students_list[num_students:]  # Remove assigned students
            assignments.append({
                "name": exam,
                "student_emails": assigned_students
            })
        return assignments

    # Assign the first 55 exams to the first 700 students
    exam_student_assignments.extend(assign_students_to_exams(group_1_exams, group_1_students))

    # Assign the remaining 25 exams to the last 300 students
    exam_student_assignments.extend(assign_students_to_exams(group_2_exams, group_2_students))

    return exam_student_assignments

# Create the assignments
assignments = create_exam_student_assignments(exams, student_emails)

# Save the result to a new JSON file
with open('exam_student_assignments.json', 'w') as f:
    json.dump(assignments, f, indent=4)

print("Assignment file 'exam_student_assignments.json' has been created.")
