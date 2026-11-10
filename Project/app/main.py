from fastapi import FastAPI, Depends
from app.routers import students, marks, reports
from app.auth.api_key import get_current_school
from app.auth import routes as auth
from app.auth.rate_limit import rate_limit

app = FastAPI(
    title="Student Management API",
    description="API for managing students and their marks",
)

app.include_router(
    students.router,
    prefix="/api/v1",
    dependencies=[
        Depends(get_current_school),
        Depends(rate_limit)
    ]
)

app.include_router(
    marks.router,
    prefix="/api/v1",
    dependencies=[
        Depends(get_current_school),
        Depends(rate_limit)
    ]
)

app.include_router(
    reports.router,
    prefix="/api/v1",
    dependencies=[
        Depends(get_current_school),
        Depends(rate_limit)
    ]
)

app.include_router(auth.router)