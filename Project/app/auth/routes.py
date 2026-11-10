from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.orm_database import get_db
from app.models import ApiUser, School
from app.schemas.auth import LoginRequest, TokenResponse
from app.auth.api_key import get_current_school
from app.auth.security import verify_password, create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
    school: School = Depends(get_current_school),
):
    # Find the user belonging to the authenticated school
    user = (
        db.query(ApiUser)
        .filter(
            ApiUser.username == login_data.username,
            ApiUser.school_id == school.id
        )
        .first()
    )

    # Verify username and password
    if not user or not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Generate JWT token
    token = create_access_token({
        "user_id": user.id,
        "username": user.username,
        "school_id": user.school_id,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }