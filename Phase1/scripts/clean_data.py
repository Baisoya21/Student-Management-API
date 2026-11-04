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


def main():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM raw_students")
        students = cursor.fetchall()

        for student in students:
            cleaned_student = clean_student(student)

            print("\n" + "=" * 60)
            print("ORIGINAL STUDENT DATA:")
            print(student)

            print("\nCLEANED STUDENT DATA:")
            print(cleaned_student)

        cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    main()
