from app.database import get_connection


def create_student(student_data):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        INSERT INTO students (
            school_id,
            roll_no,
            first_name,
            last_name,
            father_name,
            `class`,
            section,
            email,
            date_of_birth
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        student_data.school_id,
        student_data.roll_no,
        student_data.first_name,
        student_data.last_name,
        student_data.father_name,
        student_data.class_name,
        student_data.section,
        student_data.email,
        student_data.date_of_birth,
    )

    try:
        cursor.execute(
            "SELECT id FROM schools WHERE id = %s",
            (student_data.school_id,)
        )

        school = cursor.fetchone()

        if school is None:
            return None

        cursor.execute(query, values)
        connection.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        connection.close()


def get_all_students(
    page: int = 1,
    limit: int = 20,
    search: str = "",
    class_name: str = "",
    section: str = "",
    sort_field: str = "",
    include_inactive: bool = False
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        offset = (page - 1) * limit

        # Include active students by default.
        conditions = []
        filter_values = []

        if not include_inactive:
            conditions.append("is_active = 1")

        # Search by first name, last name, or father's name.
        if search:
            conditions.append("""
                (
                    first_name LIKE %s
                    OR last_name LIKE %s
                    OR father_name LIKE %s
                )
            """)

            search_pattern = f"%{search}%"

            filter_values.extend([
                search_pattern,
                search_pattern,
                search_pattern
            ])

        # Filter by class.
        if class_name:
            conditions.append("`class` = %s")
            filter_values.append(class_name)

        # Filter by section.
        if section:
            conditions.append("section = %s")
            filter_values.append(section)

        # Build the WHERE clause.
        where_clause = " AND ".join(conditions)

        if not where_clause:
            where_clause = "1 = 1"

        # Count matching students.
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM students
            WHERE {where_clause}
        """

        cursor.execute(count_query, tuple(filter_values))
        total = cursor.fetchone()["total"]

        # Set default sorting.
        sort_by = "id"
        sort_order = "ASC"

        if sort_field:
            if sort_field.startswith("-"):
                sort_by = sort_field[1:]
                sort_order = "DESC"
            else:
                sort_by = sort_field

        # Allow only approved sorting columns.
        allowed_sort_fields = {
            "id",
            "first_name",
            "last_name",
            "roll_no",
            "class",
            "section"
        }

        if sort_by not in allowed_sort_fields:
            sort_by = "id"
            sort_order = "ASC"

        # Retrieve the requested page.
        students_query = f"""
            SELECT *
            FROM students
            WHERE {where_clause}
            ORDER BY `{sort_by}` {sort_order}
            LIMIT %s OFFSET %s
        """

        values = filter_values + [limit, offset]

        cursor.execute(students_query, tuple(values))
        items = cursor.fetchall()

        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total
        }

    finally:
        cursor.close()
        connection.close()


def get_student_by_id(student_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                id,
                school_id,
                roll_no,
                first_name,
                last_name,
                father_name,
                `class`,
                section,
                email,
                date_of_birth,
                is_active,
                created_at,
                updated_at
            FROM students
            WHERE id = %s
              AND is_active = 1
        """

        cursor.execute(query, (student_id,))
        student = cursor.fetchone()

        return student

    finally:
        cursor.close()
        connection.close()


def update_student(student_id, student_data):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM students WHERE id = %s AND is_active = 1",
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None:
            return None

        query = """
            UPDATE students
            SET
                school_id = %s,
                roll_no = %s,
                first_name = %s,
                last_name = %s,
                father_name = %s,
                `class` = %s,
                section = %s,
                email = %s,
                date_of_birth = %s
            WHERE id = %s AND is_active = 1
        """

        values = (
            student_data.school_id,
            student_data.roll_no,
            student_data.first_name,
            student_data.last_name,
            student_data.father_name,
            student_data.class_name,
            student_data.section,
            student_data.email,
            student_data.date_of_birth,
            student_id,
        )

        cursor.execute(query, values)
        connection.commit()

        return student_id

    finally:
        cursor.close()
        connection.close()


def patch_student(student_id, student_data):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM students WHERE id = %s AND is_active = 1",
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None:
            return None

        updates = student_data.model_dump(
            exclude_unset=True,
            by_alias=True
        )

        if not updates:
            return student_id

        allowed_columns = {
            "school_id",
            "roll_no",
            "first_name",
            "last_name",
            "father_name",
            "class",
            "section",
            "email",
            "date_of_birth",
        }

        set_parts = []
        values = []

        for column, value in updates.items():
            if column not in allowed_columns:
                continue

            set_parts.append(f"`{column}` = %s")
            values.append(value)

        if not set_parts:
            return student_id

        query = f"""
            UPDATE students
            SET {", ".join(set_parts)}
            WHERE id = %s AND is_active = 1
        """

        values.append(student_id)

        cursor.execute(query, tuple(values))
        connection.commit()

        return student_id

    finally:
        cursor.close()
        connection.close()


def delete_student(student_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM students WHERE id = %s AND is_active = 1",
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None:
            return None

        cursor.execute(
            "UPDATE students SET is_active = 0 WHERE id = %s",
            (student_id,)
        )

        connection.commit()

        return student_id

    finally:
        cursor.close()
        connection.close()
