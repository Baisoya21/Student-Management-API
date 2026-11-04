from fastapi import APIRouter, HTTPException, status , Query
from app.schemas.students import StudentCreate, StudentUpdate , StudentPatch
from app.repositories.students import create_student, get_all_students ,get_student_by_id ,update_student ,patch_student ,delete_student
from app.repositories.reports import get_student_report_data
from app.services.reports import generate_report_card

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.get("")
def list_students(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: str = Query(default=""),
    class_name: str = Query(default="", alias="class"),
    section: str = Query(default=""),
    sort: str = Query(default=""),
    include_inactive: bool = Query(default=False)
):
    try:
        students = get_all_students(
            page,
            limit,
            search,
            class_name,
            section,
            sort,
            include_inactive
        )
        return students
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve students"
        ) from error



@router.get("/{student_id}")
def get_student(student_id: int):
    try:
        student = get_student_by_id(student_id)

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student {student_id} not found"
                }
            )

        return student

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve student"
        ) from error



@router.get("/{student_id}/report-card")
def get_report_card(
    student_id: int,
    exam: str = Query(default="Final", min_length=1)
):
    try:
        # Step 1: Get student details and exam marks from database
        student_data = get_student_report_data(student_id, exam)

        # Step 2: Check whether the student exists
        if student_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Active student {student_id} not found"
                }
            )

        # Step 3: Generate the report card
        report_card = generate_report_card(student_data, exam)

        # Step 4: Return the report card
        return report_card

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report card"
        ) from error



@router.post("", status_code=status.HTTP_201_CREATED)
def add_student(student: StudentCreate):
    try:
        student_id = create_student(student)

        if student_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SCHOOL_NOT_FOUND",
                    "message": f"School {student.school_id} not found"
                }
            )

        return {
            "message": "Student created successfully",
            "student_id": student_id
        }

    except HTTPException:
        raise

    except Exception as error:
        error_message = str(error).lower()

        if "uq_students_school_roll" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "DUPLICATE_ROLL_NUMBER",
                    "message": "This roll number already exists in this school"
                }
            ) from error

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create student"
        ) from error




@router.put("/{student_id}")
def replace_student(student_id: int, student: StudentUpdate):
    try:
        updated_student_id = update_student(student_id, student)

        if updated_student_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student {student_id} not found"
                }
            )

        return {
            "message": "Student updated successfully",
            "student_id": updated_student_id
        }

    except HTTPException:
        raise

    except Exception as error:
        error_message = str(error).lower()

        if "uq_students_school_roll" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "DUPLICATE_ROLL_NUMBER",
                    "message": "This roll number already exists in this school"
                }
            ) from error

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update student"
        ) from error



@router.patch("/{student_id}")
def partially_update_student(student_id: int, student: StudentPatch):
    try:
        updated_id = patch_student(student_id, student)

        if updated_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student {student_id} not found"
                }
            )

        return {
            "message": "Student partially updated successfully",
            "student_id": updated_id
        }

    except HTTPException:
        raise

    except Exception as error:
        error_message = str(error).lower()

        if "uq_students_school_roll" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "DUPLICATE_ROLL_NUMBER",
                    "message": "This roll number already exists in this school"
                }
            ) from error

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to partially update student"
        ) from error



@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_student(student_id: int):
    try:
        deleted_id = delete_student(student_id)

        if deleted_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student {student_id} not found"
                }
            )

        return None

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete student"
        ) from error