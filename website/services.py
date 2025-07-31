from __future__ import annotations
from website.extensions import db
from website.models import Student, GradeLevel, Subject, StudentSubject, db

def auto_enroll_subjects(student: Student):
    # Get the class name (e.g., "Grade 1", "PP2", etc.)
    class_name = student.classroom.class_name

    # Find matching grade level
    grade_level = GradeLevel.query.filter_by(name=class_name).first()

    if not grade_level:
        print(f"⚠️ No grade level found for '{class_name}'")
        return

    # Enroll the student in all subjects linked to that grade level
    for subject in grade_level.subjects:
        exists = StudentSubject.query.filter_by(student_id=student.id, subject_id=subject.id).first()
        if not exists:
            db.session.add(StudentSubject(student_id=student.id, subject_id=subject.id))

    db.session.commit()
    print(f"✅ Enrolled {student.full_name} to {len(grade_level.subjects)} subjects.")
    return render_template('errors/404.html'), 404
    return None

