from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.orm_database import get_db
from app.auth.api_key import get_current_school
from app.models import School
from app.repositories.reports import (
    get_toppers,
    get_subject_toppers,
    get_class_average,
    get_rank_list,
    get_failing_students,
    get_student_improvement,
    get_students_without_marks,
    get_data_quality_report,
)
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/toppers")
def toppers_report(
    exam: str = Query(default="Final", min_length=1),
    limit: int = Query(default=3, ge=1, le=100),
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    return get_toppers(
        db=db,
        exam=exam,
        school_id=school.id,
        limit=limit,
    )


@router.get("/subject-toppers")
def subject_toppers_report(
    exam: str = Query(default="Final", min_length=1),
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    return get_subject_toppers(
        db=db,
        exam=exam,
        school_id=school.id,
    )


@router.get("/class-average")
def class_average_report(
    class_name: str = Query(alias="class", min_length=1),
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    return get_class_average(
        db=db,
        class_name=class_name,
        school_id=school.id,
    )


@router.get("/rank-list")
def rank_list_report(
    class_name: str = Query(alias="class", min_length=1),
    exam: str = Query(default="Final", min_length=1),
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    return get_rank_list(
        db=db,
        class_name=class_name,
        exam=exam,
        school_id=school.id,
    )


@router.get("/failing")
def failing_students(
    exam: str = Query(default="Final", min_length=1),
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    return get_failing_students(
        db=db,
        exam=exam,
        school_id=school.id,
    )


@router.get("/improvement")
def student_improvement_report(
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    return get_student_improvement(
        db=db,
        school_id=school.id,
    )


@router.get("/no-marks")
def students_without_marks_report(
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    return get_students_without_marks(
        db=db,
        school_id=school.id,
    )


@router.get("/data-quality")
def data_quality_report(
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    return get_data_quality_report(
        db=db,
        school_id=school.id,
    )
