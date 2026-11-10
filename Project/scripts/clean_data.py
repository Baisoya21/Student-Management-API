
from app.database import get_connection

from app.cleaning.cleaners import (
    clean_school_code,
    clean_roll_no,
    clean_student_names,
    clean_father_name,
    clean_class,
    clean_section,
    clean_email,
    clean_date_of_birth,
)


def clean_student(student):
    first_name, last_name = clean_student_names(
        student["first_name"],
        student["last_name"],
    )

    cleaned_student = {
        "raw_id": student["raw_id"],
        "school_code": clean_school_code(student["school_code"]),
        "roll_no": clean_roll_no(student["roll_no"]),
        "first_name": first_name,
        "last_name": last_name,
        "father_name": clean_father_name(student["father_name"]),
        "class": clean_class(student["class"]),
        "section": clean_section(student["section"]),
        "email": clean_email(student["email"]),
        "date_of_birth": clean_date_of_birth(student["date_of_birth"]),
    }

    return cleaned_student


def audit_cleaning(students):
    total = len(students)
    valid = 0

    issues = {
        "invalid_school_code": 0,
        "invalid_roll_no": 0,
        "missing_first_name": 0,
        "invalid_class": 0,
        "invalid_section": 0,
    }

    for student in students:
        cleaned = clean_student(student)

        if cleaned["school_code"] is None:
            issues["invalid_school_code"] += 1

        if cleaned["roll_no"] is None:
            issues["invalid_roll_no"] += 1

        if cleaned["first_name"] is None:
            issues["missing_first_name"] += 1

        if cleaned["class"] is None:
            issues["invalid_class"] += 1

        if cleaned["section"] is None:
            issues["invalid_section"] += 1

        if all([
            cleaned["school_code"],
            cleaned["roll_no"],
            cleaned["first_name"],
            cleaned["class"],
            cleaned["section"],
        ]):
            valid += 1

    print("\n" + "=" * 50)
    print("          CLEANING AUDIT REPORT")
    print("=" * 50)

    print("Total raw records:", total)
    print("Records passing required-field checks:", valid)
    print("Records failing required-field checks:", total - valid)

    print("\nIndividual cleaning issues:")

    for issue, count in issues.items():
        print(f"{issue}: {count}")

    print("=" * 50)


def check_cleaned_duplicates(students):
    seen = {}

    for student in students:
        cleaned = clean_student(student)

        school_code = cleaned["school_code"]
        roll_no = cleaned["roll_no"]

        if not school_code or not roll_no:
            continue

        # Match the INT column in the final students table
        roll_no = int(roll_no)

        key = (school_code, roll_no)

        if key in seen:
            print(
                f"Duplicate found: School={school_code}, "
                f"Roll No={roll_no}, "
                f"Raw IDs={seen[key]} and {student['raw_id']}"
            )
        else:
            seen[key] = student["raw_id"]


def show_invalid_records(students):
    print("\nINVALID RECORDS")
    print("=" * 50)

    for student in students:
        cleaned = clean_student(student)

        problems = []

        if not cleaned["school_code"]:
            problems.append("Invalid school code")

        if not cleaned["roll_no"]:
            problems.append("Invalid roll number")

        if not cleaned["first_name"]:
            problems.append("Missing first name")

        if not cleaned["class"]:
            problems.append("Invalid class")

        if not cleaned["section"]:
            problems.append("Invalid section")

        if problems:
            print(
                f"Raw ID: {student['raw_id']} | "
                f"Issues: {', '.join(problems)}"
            )


def check_existing_student_conflicts(students):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT school_id, roll_no, id, first_name, last_name
            FROM students
        """)

        existing_students = cursor.fetchall()

        existing_keys = {
            (row["school_id"], row["roll_no"]): row
            for row in existing_students
        }

        school_mapping = {
            "GPS": 1,
            "SVS": 2
        }

        print("\nEXISTING STUDENT CONFLICTS")
        print("=" * 50)

        for student in students:
            cleaned = clean_student(student)

            school_id = school_mapping.get(cleaned["school_code"])
            roll_no = cleaned["roll_no"]

            if not school_id or not roll_no:
                continue

            key = (school_id, int(roll_no))

            if key in existing_keys:
                existing = existing_keys[key]

                print(
                    f"Raw ID: {student['raw_id']} | "
                    f"School ID: {school_id} | "
                    f"Roll No: {roll_no} | "
                    f"Existing Student ID: {existing['id']} | "
                    f"Existing Name: {existing['first_name']} "
                    f"{existing['last_name']}"
                )

        cursor.close()

    finally:
        connection.close()

def main():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM raw_students")
        students = cursor.fetchall()

        # Run cleaning audit
        audit_cleaning(students)
        check_cleaned_duplicates(students)
        show_invalid_records(students)
        check_existing_student_conflicts(students)

        ''' Original cleaning preview
        for student in students:
            cleaned_student = clean_student(student)

            print("\n" + "=" * 60)
            print("ORIGINAL STUDENT DATA:")
            print(student)

            print("\nCLEANED STUDENT DATA:")
            print(cleaned_student)'''

        cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    main()
