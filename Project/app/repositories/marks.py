from app.database import get_connection

def create_mark(student_id, mark_data, school_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check whether the student belongs to this school.
        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE id = %s
              AND school_id = %s
              AND is_active = 1
            """,
            (student_id, school_id)
        )

        student = cursor.fetchone()

        if student is None:
            return None

        mark_values = mark_data.model_dump()

        cursor.execute(
            """
            INSERT INTO marks (
                student_id,
                subject,
                exam,
                marks_obtained,
                max_marks,
                is_absent
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                student_id,
                mark_values["subject"],
                mark_values["exam"],
                mark_values["marks_obtained"],
                mark_values["max_marks"],
                mark_values["is_absent"],
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        connection.close()



def get_marks_by_student_id(student_id, school_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                m.id,
                m.student_id,
                m.subject,
                m.exam,
                m.marks_obtained,
                m.max_marks,
                m.is_absent
            FROM marks m
            JOIN students s
                ON m.student_id = s.id
            WHERE m.student_id = %s
              AND s.school_id = %s
            ORDER BY m.id
            """,
            (student_id, school_id)
        )

        marks = cursor.fetchall()

        return marks

    finally:
        cursor.close()
        connection.close()


def update_mark(mark_id, mark_data, school_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Retrieve the existing marks record
        cursor.execute(
    """
    SELECT
        m.id,
        m.marks_obtained,
        m.max_marks
    FROM marks m
    JOIN students s
        ON m.student_id = s.id
    WHERE m.id = %s
      AND s.school_id = %s
    """,
    (mark_id, school_id)
)

        mark = cursor.fetchone()

        if mark is None:
            return None

        # Get only the fields supplied in the PATCH request
        updates = mark_data.model_dump(exclude_unset=True)

        if not updates:
            return mark_id

        # Determine the final marks and maximum marks after the update
        final_marks = updates.get(
            "marks_obtained",
            mark["marks_obtained"]
        )

        final_max_marks = updates.get(
            "max_marks",
            mark["max_marks"]
        )

        # Validate marks against the final maximum
        if (
            final_marks is not None
            and final_max_marks is not None
            and final_marks > final_max_marks
        ):
            raise ValueError(
                "marks_obtained cannot exceed max_marks"
            )

        allowed_columns = {
            "subject",
            "exam",
            "marks_obtained",
            "max_marks",
            "is_absent",
        }

        set_parts = []
        values = []

        for column, value in updates.items():
            if column not in allowed_columns:
                continue

            set_parts.append(f"`{column}` = %s")
            values.append(value)

        if not set_parts:
            return mark_id

        query = f"""
        UPDATE marks m
        JOIN students s
        ON m.student_id = s.id
        SET {", ".join(set_parts)}
        WHERE m.id = %s
        AND s.school_id = %s
"""

        values.extend([mark_id, school_id])

        cursor.execute(query, tuple(values))
        connection.commit()

        return mark_id

    finally:
        cursor.close()
        connection.close()


def delete_mark(mark_id: int, school_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check whether the mark exists
        cursor.execute(
            """
            SELECT m.id
            FROM marks m
            JOIN students s
            ON m.student_id = s.id
            WHERE m.id = %s
            AND s.school_id = %s
            """,
    (mark_id, school_id)
)

        mark = cursor.fetchone()

        if mark is None:
            return None

        # Delete the mark
        cursor.execute(
            """
            DELETE m
            FROM marks m
            JOIN students s
            ON m.student_id = s.id
            WHERE m.id = %s
            AND s.school_id = %s
            """,
    (mark_id, school_id)
)

        connection.commit()

        return mark_id

    finally:
        cursor.close()
        connection.close()