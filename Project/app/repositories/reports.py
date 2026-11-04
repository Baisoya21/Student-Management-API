from app.database import get_connection
from sqlalchemy import select, func , text
from sqlalchemy.orm import Session

from app.models import Student, Mark


def get_student_report_data(student_id: int, exam: str):
    # Will Retrieve an active student's details and marks for a particular exam.


    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check whether the student exists and is active.
        cursor.execute(
            """
            SELECT
                id,
                school_id,
                roll_no,
                first_name,
                last_name,
                `class`,
                section
            FROM students
            WHERE id = %s AND is_active = 1
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None:
            return None

        # Retrieve marks for the requested exam.
        cursor.execute(
            """
            SELECT
                subject,
                exam,
                marks_obtained,
                max_marks
            FROM marks
            WHERE student_id = %s
              AND exam = %s
            ORDER BY subject
            """,
            (student_id, exam)
        )

        marks = cursor.fetchall()

        return {
            "student": student,
            "marks": marks
        }

    finally:
        cursor.close()
        connection.close()



def get_toppers(db: Session, exam: str, limit: int = 3):
    # Calculate each student's overall percentage.
    percentage = (
        func.sum(Mark.marks_obtained)
        / func.nullif(func.sum(Mark.max_marks), 0)
        * 100
    )

    # Fetch students and calculate their percentages for the selected exam.
    statement = (
        select(
            Student.id.label("student_id"),
            Student.first_name,
            Student.last_name,
            Student.class_name,
            Student.section,
            percentage.label("percentage"),
        )
        .join(Mark, Mark.student_id == Student.id)
        .where(
            Student.is_active.is_(True),
            Mark.exam == exam,
            Mark.is_absent.is_(False),
            Mark.marks_obtained.is_not(None),
        )
        .group_by(
            Student.id,
            Student.first_name,
            Student.last_name,
            Student.class_name,
            Student.section,
        )
        .order_by(
            Student.class_name,
            percentage.desc(),
            Student.id,
        )
    )

    # Execute the SQLAlchemy query.
    rows = db.execute(statement).mappings().all()

    # Store the top students separately for each class.
    toppers_by_class = {}

    for row in rows:
        class_name = row["class_name"]

        if class_name not in toppers_by_class:
            toppers_by_class[class_name] = []

        if len(toppers_by_class[class_name]) < limit:
            toppers_by_class[class_name].append(
                {
                    "student_id": row["student_id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "class": class_name,
                    "section": row["section"],
                    "percentage": round(float(row["percentage"]), 2),
                }
            )

    return toppers_by_class


def get_subject_toppers(db: Session, exam: str):
    # Calculate the percentage obtained in each subject.
    percentage = (
        Mark.marks_obtained
        / func.nullif(Mark.max_marks, 0)
        * 100
    )

    # Retrieve students' marks for the selected exam.
    statement = (
        select(
            Student.id.label("student_id"),
            Student.first_name,
            Student.last_name,
            Student.class_name,
            Student.section,
            Mark.subject,
            Mark.marks_obtained,
            Mark.max_marks,
            percentage.label("percentage"),
        )
        .join(Mark, Mark.student_id == Student.id)
        .where(
            Student.is_active.is_(True),
            Mark.exam == exam,
            Mark.is_absent.is_(False),
            Mark.marks_obtained.is_not(None),
        )
        .order_by(
            Mark.subject,
            percentage.desc(),
            Student.id,
        )
    )

    rows = db.execute(statement).mappings().all()

    subject_toppers = {}

    # Keep the highest-scoring student for each subject.
    for row in rows:
        subject = row["subject"]

        if subject not in subject_toppers:
            subject_toppers[subject] = {
                "student_id": row["student_id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "class": row["class_name"],
                "section": row["section"],
                "subject": subject,
                "marks_obtained": float(row["marks_obtained"]),
                "max_marks": float(row["max_marks"]),
                "percentage": round(float(row["percentage"]), 2),
            }

    return subject_toppers



def get_class_average(db: Session, class_name: str):
    # Calculate the average marks for each subject.
    average_marks = func.avg(Mark.marks_obtained)

    # Select the subject and its average marks.
    statement = (
        select(
            Mark.subject,
            average_marks.label("average_marks"),
        )
        .join(Student, Student.id == Mark.student_id)
        .where(
            Student.is_active.is_(True),
            Student.class_name == class_name,
            Mark.is_absent.is_(False),
            Mark.marks_obtained.is_not(None),
        )
        .group_by(Mark.subject)
        .order_by(Mark.subject)
    )

    # Execute the query.
    rows = db.execute(statement).mappings().all()

    # Format the results.
    return {
        row["subject"]: round(float(row["average_marks"]), 2)
        for row in rows
    }


def get_rank_list(db: Session, class_name: str, exam: str):
    # Calculate each student's overall percentage.
    percentage = (
        func.sum(Mark.marks_obtained)
        / func.nullif(func.sum(Mark.max_marks), 0)
        * 100
    )

    # Retrieve students and calculate their percentages.
    statement = (
        select(
            Student.id.label("student_id"),
            Student.first_name,
            Student.last_name,
            Student.class_name,
            Student.section,
            percentage.label("percentage"),
        )
        .join(Mark, Mark.student_id == Student.id)
        .where(
            Student.is_active.is_(True),
            Student.class_name == class_name,
            Mark.exam == exam,
            Mark.is_absent.is_(False),
            Mark.marks_obtained.is_not(None),
        )
        .group_by(
            Student.id,
            Student.first_name,
            Student.last_name,
            Student.class_name,
            Student.section,
        )
        .order_by(
            percentage.desc(),
            Student.id,
        )
    )

    rows = db.execute(statement).mappings().all()

    rank_list = []
    previous_percentage = None
    current_rank = 0

    for position, row in enumerate(rows, start=1):
        student_percentage = round(float(row["percentage"]), 2)

        # Equal percentages receive equal ranks.
        if student_percentage != previous_percentage:
            current_rank = position

        rank_list.append(
            {
                "rank": current_rank,
                "student_id": row["student_id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "class": row["class_name"],
                "section": row["section"],
                "percentage": student_percentage,
            }
        )

        previous_percentage = student_percentage

    return rank_list


def get_failing_students(db: Session, exam: str):

    # Calculate the percentage obtained in each subject.
    percentage = (
        Mark.marks_obtained
        / func.nullif(Mark.max_marks, 0)
        * 100
    )

    # Retrieve students who scored below 33% in any subject.
    statement = (
        select(
            Student.id.label("student_id"),
            Student.first_name,
            Student.last_name,
            Student.class_name,
            Student.section,
            Mark.subject,
            Mark.marks_obtained,
            Mark.max_marks,
            percentage.label("percentage"),
        )
        .join(Mark, Mark.student_id == Student.id)
        .where(
            Student.is_active.is_(True),
            Mark.exam == exam,
            Mark.is_absent.is_(False),
            Mark.marks_obtained.is_not(None),
            Mark.max_marks > 0,
            percentage < 33,
        )
        .order_by(
            Student.class_name,
            Student.id,
            Mark.subject,
        )
    )

    # Execute the query.
    rows = db.execute(statement).mappings().all()

    # Format the response.
    failing_students = []

    for row in rows:
        failing_students.append(
            {
                "student_id": row["student_id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "class": row["class_name"],
                "section": row["section"],
                "failed_subject": row["subject"],
                "marks_obtained": float(row["marks_obtained"]),
                "max_marks": float(row["max_marks"]),
                "percentage": round(float(row["percentage"]), 2),
            }
        )

    return failing_students


def get_student_improvement(db: Session):

    # Calculate each student's Mid-Term percentage.
    mid_term_percentage = (
        select(
            Mark.student_id,
            (
                func.sum(Mark.marks_obtained)
                / func.nullif(func.sum(Mark.max_marks), 0)
                * 100
            ).label("percentage")
        )
        .where(
            Mark.exam == "Mid-Term",
            Mark.is_absent.is_(False),
            Mark.marks_obtained.is_not(None),
            Mark.max_marks > 0,
        )
        .group_by(Mark.student_id)
        .subquery()
    )

    # Calculate each student's Final percentage.
    final_percentage = (
        select(
            Mark.student_id,
            (
                func.sum(Mark.marks_obtained)
                / func.nullif(func.sum(Mark.max_marks), 0)
                * 100
            ).label("percentage")
        )
        .where(
            Mark.exam == "Final",
            Mark.is_absent.is_(False),
            Mark.marks_obtained.is_not(None),
            Mark.max_marks > 0,
        )
        .group_by(Mark.student_id)
        .subquery()
    )

    # Compare both exam percentages for each student.
    improvement = (
        final_percentage.c.percentage
        - mid_term_percentage.c.percentage
    )

    statement = (
        select(
            Student.id.label("student_id"),
            Student.first_name,
            Student.last_name,
            Student.class_name,
            Student.section,
            mid_term_percentage.c.percentage.label("mid_term_percentage"),
            final_percentage.c.percentage.label("final_percentage"),
            improvement.label("improvement"),
        )
        .join(
            mid_term_percentage,
            mid_term_percentage.c.student_id == Student.id,
        )
        .join(
            final_percentage,
            final_percentage.c.student_id == Student.id,
        )
        .where(
            Student.is_active.is_(True),
            improvement > 0,
        )
        .order_by(improvement.desc())
    )

    # Execute the query.
    rows = db.execute(statement).mappings().all()

    # Format the response.
    return [
        {
            "student_id": row["student_id"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "class": row["class_name"],
            "section": row["section"],
            "mid_term_percentage": round(float(row["mid_term_percentage"]), 2),
            "final_percentage": round(float(row["final_percentage"]), 2),
            "improvement": round(float(row["improvement"]), 2),
        }
        for row in rows
    ]


def get_students_without_marks(db: Session):

    # Find active students who do not have any marks.
    statement = (
        select(
            Student.id.label("student_id"),
            Student.first_name,
            Student.last_name,
            Student.class_name,
            Student.section,
        )
        .where(
            Student.is_active.is_(True),
            ~Student.id.in_(
                select(Mark.student_id)
            ),
        )
        .order_by(Student.id)
    )

    # Execute the query.
    rows = db.execute(statement).mappings().all()

    # Format the response.
    return [
        {
            "student_id": row["student_id"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "class": row["class_name"],
            "section": row["section"],
        }
        for row in rows
    ]


def get_data_quality_report(db: Session):
    student_counts = db.execute(
        text("""
            SELECT
                COALESCE(SUM(CASE WHEN last_name IS NULL THEN 1 ELSE 0 END), 0)
                    AS missing_last_name,

                COALESCE(SUM(CASE WHEN father_name IS NULL THEN 1 ELSE 0 END), 0)
                    AS missing_father_name,

                COALESCE(SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END), 0)
                    AS missing_email

            FROM students
        """)
    ).mappings().one()

    rejected_count = db.execute(
        text("""
            SELECT COUNT(*) AS rejected_rows
            FROM rejected_students
        """)
    ).mappings().one()

    return {
        "missing_last_name": student_counts["missing_last_name"],
        "missing_father_name": student_counts["missing_father_name"],
        "missing_email": student_counts["missing_email"],
        "rejected_rows": rejected_count["rejected_rows"]
    }