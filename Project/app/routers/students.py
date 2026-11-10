from fastapi import APIRouter, HTTPException, status, Query, Depends
from app.schemas.students import StudentCreate, StudentUpdate, StudentPatch
from app.repositories.students import (
    create_student,
    get_all_students,
    get_student_by_id,
    update_student,
    patch_student,
    delete_student,
)
from app.repositories.reports import get_student_report_data
from app.services.reports import generate_report_card
from app.auth.api_key import get_current_school
from app.models import School
from app.auth.dependencies import get_current_user
from app.auth.dependencies import require_admin


router = APIRouter(
    prefix="/students",
    tags=["Students"],
    dependencies=[Depends(get_current_user)]
)


@router.get("")
def list_students(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: str = Query(default=""),
    class_name: str = Query(default="", alias="class"),
    section: str = Query(default=""),
    sort: str = Query(default=""),
    include_inactive: bool = Query(default=False),
    school: School = Depends(get_current_school)
):
    try:
        students = get_all_students(
            school.id,
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
def get_student(
    student_id: int,
    school: School = Depends(get_current_school)
):
    try:
        student = get_student_by_id(student_id, school.id)

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
    exam: str = Query(default="Final", min_length=1),
    school: School = Depends(get_current_school)
):
    try:
        # Retrieve student details and marks for this school.
        student_data = get_student_report_data(
            student_id,
            exam,
            school.id
        )

        if student_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Active student {student_id} not found"
                }
            )

        report_card = generate_report_card(student_data, exam)

        return report_card

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report card"
        ) from error



@router.post("", status_code=status.HTTP_201_CREATED)
def add_student(
    student: StudentCreate,
    school: School = Depends(get_current_school),
    current_user = Depends(require_admin)
):
    try:
        student_id = create_student(student, school.id)

        if student_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SCHOOL_NOT_FOUND",
                    "message": "Authenticated school not found"
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
def replace_student(
    student_id: int,
    student: StudentUpdate,
    school: School = Depends(get_current_school),
    current_user = Depends(require_admin)
):
    try:
        updated_student_id = update_student(
            student_id,
            student,
            school.id
        )

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
def partially_update_student(
    student_id: int,
    student: StudentPatch,
    school: School = Depends(get_current_school),
    current_user = Depends(require_admin)
):
    try:
        updated_id = patch_student(
            student_id,
            student,
            school.id
        )

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
def remove_student(
    student_id: int,
    school: School = Depends(get_current_school),
    current_user = Depends(require_admin)
):
    try:
        deleted_id = delete_student(student_id, school.id)

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
