from app.database import get_connection


def create_mark(student_id, mark_data):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check whether the student exists and is active
        cursor.execute(
            "SELECT id FROM students WHERE id = %s AND is_active = 1",
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None:
            return None

        # Prepare the mark values
        mark_values = mark_data.model_dump()

        # Insert the mark into the database
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


def get_marks_by_student_id(student_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                student_id,
                subject,
                exam,
                marks_obtained,
                max_marks,
                is_absent
            FROM marks
            WHERE student_id = %s
            ORDER BY id
            """,
            (student_id,)
        )

        marks = cursor.fetchall()

        return marks

    finally:
        cursor.close()
        connection.close()


def update_mark(mark_id, mark_data):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Retrieve the existing marks record
        cursor.execute(
            """
            SELECT id, marks_obtained, max_marks
            FROM marks
            WHERE id = %s
            """,
            (mark_id,)
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
            UPDATE marks
            SET {", ".join(set_parts)}
            WHERE id = %s
        """

        values.append(mark_id)

        cursor.execute(query, tuple(values))
        connection.commit()

        return mark_id

    finally:
        cursor.close()
        connection.close()


def delete_mark(mark_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check whether the mark exists
        cursor.execute(
            "SELECT id FROM marks WHERE id = %s",
            (mark_id,)
        )

        mark = cursor.fetchone()

        if mark is None:
            return None

        # Delete the mark
        cursor.execute(
            "DELETE FROM marks WHERE id = %s",
            (mark_id,)
        )

        connection.commit()

        return mark_id

    finally:
        cursor.close()
        connection.close()