from app.services.grading import (
    calculate_grade,
    calculate_percentage,
    calculate_result,
)


def generate_report_card(student_data, exam):
    #Generate a report card for one student for a particular exam.

    student = student_data["student"]
    marks = student_data["marks"]

    subjects = []
    total_marks_obtained = 0
    total_max_marks = 0

    for mark in marks:
        marks_obtained = float(mark["marks_obtained"])
        max_marks = float(mark["max_marks"])

        percentage = calculate_percentage(
            marks_obtained,
            max_marks
        )

        grade = calculate_grade(percentage)
        result = calculate_result(percentage)

        subjects.append({
            "subject": mark["subject"],
            "marks_obtained": marks_obtained,
            "max_marks": max_marks,
            "percentage": percentage,
            "grade": grade,
            "result": result,
        })

        total_marks_obtained += marks_obtained
        total_max_marks += max_marks

    if total_max_marks > 0:
        overall_percentage = calculate_percentage(
            total_marks_obtained,
            total_max_marks
        )

        overall_grade = calculate_grade(overall_percentage)
        overall_result = calculate_result(overall_percentage)

    else:
        overall_percentage = 0
        overall_grade = "F"
        overall_result = "Fail"

    return {
        "student": student,
        "exam": exam,
        "subjects": subjects,
        "total_marks_obtained": total_marks_obtained,
        "total_max_marks": total_max_marks,
        "overall_percentage": overall_percentage,
        "overall_grade": overall_grade,
        "overall_result": overall_result,
    }