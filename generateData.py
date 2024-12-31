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

    # Function to assign students to exams, making sure no exam is over or underfilled
    def assign_students_to_exams(exams_list, students_list):
        random.shuffle(students_list)  # Shuffle students for randomness
        assignments = []
        num_students = len(students_list)

        # Distribute students across exams (max 5 exams per student)
        student_exam_count = {student: 0 for student in students_list}
        exam_assignments = {exam: [] for exam in exams_list}
        
        # Function to assign a student to an exam if they haven't reached the max
        def assign_student_to_exam(student, exam):
            if student_exam_count[student] < 5:
                exam_assignments[exam].append(student)
                student_exam_count[student] += 1

        # Fill the exams with students, ensuring no one takes more than 5 exams
        for exam in exams_list:
            # Calculate the number of students needed for this exam (between 10 and 400)
            required_students = random.randint(10, 400)
            available_students = [student for student in students_list if student_exam_count[student] < 5]

            # If there are enough students to assign
            if len(available_students) >= required_students:
                random.shuffle(available_students)  # Shuffle available students for randomness
                assigned_students = available_students[:required_students]

                # Assign the selected students to this exam
                for student in assigned_students:
                    assign_student_to_exam(student, exam)

            else:
                # If there aren't enough students left, assign as many as possible without exceeding 5 exams per student
                random.shuffle(available_students)  # Shuffle available students for randomness
                assigned_students = available_students[:len(available_students)]
                for student in assigned_students:
                    assign_student_to_exam(student, exam)

        # Build the final assignment list for this set of exams
        for exam in exams_list:
            assignments.append({
                "name": exam,
                "student_emails": exam_assignments[exam]
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
