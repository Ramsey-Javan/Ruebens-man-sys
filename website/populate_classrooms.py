from website.models import db, Classroom

def populate_classrooms():
    classrooms = [
        "Playgroup", "PP1", "PP2",
        "Grade 1", "Grade 2", "Grade 3",
        "Grade 4", "Grade 5", "Grade 6",
        "Grade 7", "Grade 8", "Grade 9"
    ]

    for name in classrooms:
        exists = Classroom.query.filter_by(class_name=name).first()
        if not exists:
            db.session.add(Classroom(class_name=name))
            print(f"✅ Added classroom: {name}")
    db.session.commit()
    print("🎉 All classrooms seeded successfully.")
