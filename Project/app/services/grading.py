def calculate_grade(percentage: float) -> str:
    #Return the grade based on the student's percentage.

    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 33:
        return "D"
    else:
        return "F"


def calculate_percentage(
    marks_obtained: float,
    max_marks: float
) -> float:
    # Will Calculate percentage from marks obtained and maximum marks.

    if max_marks <= 0:
        raise ValueError("Maximum marks must be greater than zero")

    return round((marks_obtained / max_marks) * 100, 2)


def calculate_result(percentage: float) -> str:
    # Will Return Pass if percentage is at least 33; otherwise, return Fail.

    if percentage >= 33:
        return "Pass"

    return "Fail"
