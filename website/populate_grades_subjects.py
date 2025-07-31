# website/populate_grades_subjects.py

from models import db, GradeLevel, Subject
from app import create_app  # adjust import path to your app factory

app = create_app()

cbc_structure = {
    "Playgroup": [],
    "PP1": [],
    "PP2": [],
    "Grade 1": [
        "English Language Activities",
        "Kiswahili Language Activities",
        "Mathematical Activities",
        "Environmental Activities",
        "Creative Activities",
        "Religious Education Activities",
        "Movement and Creative Activities"
    ],
    "Grade 2": [
        "English Language Activities",
        "Kiswahili Language Activities",
        "Mathematical Activities",
        "Environmental Activities",
        "Creative Activities",
        "Religious Education Activities",
        "Movement and Creative Activities"
    ],
    "Grade 3": [
        "English Language Activities",
        "Kiswahili Language Activities",
        "Mathematical Activities",
        "Environmental Activities",
        "Creative Activities",
        "Religious Education Activities",
        "Movement and Creative Activities"
    ],
    "Grade 4": [
        "English",
        "Kiswahili",
        "Mathematics",
        "Religious Education",
        "Science and Technology",
        "Agriculture and Nutrition",
        "Social Studies",
        "Creative Arts"
    ],
    "Grade 5": [
        "English",
        "Kiswahili",
        "Mathematics",
        "Religious Education",
        "Science and Technology",
        "Agriculture and Nutrition",
        "Social Studies",
        "Creative Arts"
    ],
    "Grade 6": [
        "English",
        "Kiswahili",
        "Mathematics",
        "Religious Education",
        "Science and Technology",
        "Agriculture and Nutrition",
        "Social Studies",
        "Creative Arts"
    ],
    "Grade 7": [
        "English",
        "Kiswahili",
        "Mathematics",
        "Integrated Science",
        "Social Studies",
        "Religious Education",
        "Agriculture",
        "Pre-Technical Studies",
        "Creative Arts and Sports"
    ],
    "Grade 8": [
        "English",
        "Kiswahili",
        "Mathematics",
        "Integrated Science",
        "Social Studies",
        "Religious Education",
        "Agriculture",
        "Pre-Technical Studies",
        "Creative Arts and Sports"
    ],
    "Grade 9": [
        "English",
        "Kiswahili",
        "Mathematics",
        "Integrated Science",
        "Social Studies",
        "Religious Education",
        "Agriculture",
        "Pre-Technical Studies",
        "Creative Arts and Sports"
    ],
}

with app.app_context():
    print("⏳ Seeding GradeLevels and Subjects...")

    for grade_name, subjects in cbc_structure.items():
        grade_level = GradeLevel.query.filter_by(name=grade_name).first()
        if not grade_level:
            grade_level = GradeLevel(name=grade_name)
            db.session.add(grade_level)
            db.session.commit()
            print(f"✅ Added GradeLevel: {grade_name}")

        for subject_name in subjects:
            existing_subject = Subject.query.filter_by(name=subject_name, grade_level_id=grade_level.id).first()
            if not existing_subject:
                subject = Subject(name=subject_name, grade_level_id=grade_level.id)
                db.session.add(subject)
                print(f"  ➕ Added subject '{subject_name}' to {grade_name}")

    db.session.commit()
    print("🎉 Done seeding all grades and subjects.")
