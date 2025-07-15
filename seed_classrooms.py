from website import create_app, db
from website.models import Classroom, Staff

app = create_app()

standard_classes = [
    "Playgroup", "Pre-Primary 1 (PP1)", "Pre-Primary 2 (PP2)"
] + [f"Grade {i}" for i in range(1, 10)]

with app.app_context():
    teacher = Staff.query.get(1)
    if not teacher:
        dummy_teacher = Staff(
            id=1,
            full_name="Default Teacher",
            staff_id="T001",
            role="teacher",
            contact="0712345678",
            email="default.teacher@strueben.ac.ke"
        )
        db.session.add(dummy_teacher)
        db.session.commit()
        print("Dummy teacher created.")

    for class_name in standard_classes:
        existing = Classroom.query.filter_by(class_name=class_name).first()
        if not existing:
            classroom = Classroom(class_name=class_name, teacher_id=1)
            db.session.add(classroom)

    db.session.commit()
    print("Classrooms seeded successfully.")
