from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.orm_database import get_db
from app.models import School


def get_current_school(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db),
): 
    # Check whether API key was provided
    if not x_api_key:
        raise HTTPException(
        status_code=401,
        detail="API Key is required",
    )
    # Find the school using its API key
    school = (
        db.query(School)
        .filter(School.api_key == x_api_key)
        .first()
    )
    # Reject invalid API keys
    if not school:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )

    return school