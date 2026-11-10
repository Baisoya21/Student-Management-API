from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.marks import MarkCreate, MarkUpdate
from app.repositories.marks import (
    create_mark,
    get_marks_by_student_id,
    update_mark,
    delete_mark,
)
from app.auth.api_key import get_current_school
from app.models import School
from app.auth.dependencies import get_current_user
from app.auth.dependencies import require_admin

router = APIRouter(
    tags=["Marks"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/students/{student_id}/marks", status_code=status.HTTP_201_CREATED)
def add_mark(
    student_id: int,
    mark: MarkCreate,
    school: School = Depends(get_current_school),
    current_user = Depends(require_admin)
):
    try:
        mark_id = create_mark(student_id, mark, school.id)

        if mark_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student {student_id} not found"
                }
            )

        return {
            "message": "Marks added successfully",
            "mark_id": mark_id,
            "student_id": student_id
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add marks"
        ) from error


@router.get("/students/{student_id}/marks")
def get_student_marks(
    student_id: int,
    school: School = Depends(get_current_school),
    current_user = Depends(require_admin)
):
    try:
        marks = get_marks_by_student_id(student_id, school.id)
        return marks

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve student marks"
        ) from error


@router.patch("/marks/{mark_id}")
def update_student_mark(
    mark_id: int,
    mark: MarkUpdate,
    school: School = Depends(get_current_school),
    current_user = Depends(require_admin)
):
    try:
        updated_id = update_mark(mark_id, mark, school.id)

        if updated_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "MARK_NOT_FOUND",
                    "message": f"Mark {mark_id} not found"
                }
            )

        return {
            "message": "Marks updated successfully",
            "mark_id": updated_id
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error)
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update marks"
        ) from error


@router.delete("/marks/{mark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_mark(
    mark_id: int,
    school: School = Depends(get_current_school),
    current_user = Depends(require_admin)
):
    try:
        deleted_id = delete_mark(mark_id, school.id)

        if deleted_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "MARK_NOT_FOUND",
                    "message": f"Mark {mark_id} not found"
                }
            )

        return

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete marks"
        ) from error
