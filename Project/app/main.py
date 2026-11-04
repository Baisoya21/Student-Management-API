from fastapi import FastAPI
from app.routers import students , marks , reports

app = FastAPI(
    title="Student Management API",
    description="API for managing students and their marks",
)

app.include_router(
    students.router,
    prefix="/api/v1"
)

app.include_router(
    marks.router,
    prefix="/api/v1"
)

app.include_router(
    reports.router,
    prefix="/api/v1"
)