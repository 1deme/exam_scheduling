import json
import random

# Load data from the JSON files
with open('exams.json', 'r') as exams_file:
    exams = json.load(exams_file)

with open('studentMails.json', 'r') as students_file:
    student_emails = json.load(students_file)

# List to store the results
output_data = []

# Split exams into two groups: overlapping and non-overlapping
num_exams = len(exams)
overlapping_exams = exams[:num_exams // 2]
non_overlapping_exams = exams[num_exams // 2:]

# Create a pool of shared students for overlapping exams
shared_students_pool = random.sample(student_emails, k=random.randint(50, 100))

# Assign students to overlapping exams
for exam in overlapping_exams:
    exam_name = exam["name"]
    num_students = random.randint(10, 300)

    # Combine shared students with unique ones
    shared_emails = random.sample(shared_students_pool, k=min(len(shared_students_pool), random.randint(5, 20)))
    unique_emails = random.sample(student_emails, k=num_students - len(shared_emails))
    assigned_emails = shared_emails + unique_emails

    # Shuffle to make the distribution look more natural
    random.shuffle(assigned_emails)

    output_data.append({
        "name": exam_name,
        "student_emails": assigned_emails
    })

# Assign students to non-overlapping exams
for exam in non_overlapping_exams:
    exam_name = exam["name"]
    num_students = random.randint(10, 300)

    # Assign entirely unique students
    assigned_emails = random.sample(student_emails, k=num_students)

    output_data.append({
        "name": exam_name,
        "student_emails": assigned_emails
    })

# Write the output to a JSON file
with open('exam_student_assignments.json', 'w') as output_file:
    json.dump(output_data, output_file, indent=4)

print("Generated exam_student_assignments.json")
