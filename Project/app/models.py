from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    CHAR,
    text,
    func,
)

from app.orm_database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id"),
        nullable=False,
    )

    roll_no = Column(Integer, nullable=False)

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    father_name = Column(String(100), nullable=True)

    class_name = Column("class", String(5), nullable=False)
    section = Column(CHAR(1), nullable=False)

    email = Column(String(120), nullable=True)
    date_of_birth = Column(Date, nullable=True)

    is_active = Column(
        Boolean,
        nullable=False,
        server_default=text("1"),
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, autoincrement=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False,
    )

    subject = Column(String(30), nullable=False)
    exam = Column(String(20), nullable=False)

    marks_obtained = Column(Numeric(5, 2), nullable=True)

    max_marks = Column(
        Numeric(5, 2),
        nullable=False,
        server_default=text("100.00"),
    )

    is_absent = Column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    city = Column(String(50), nullable=False)

    api_key = Column(String(64), nullable=False, unique=True)
    contact_email = Column(String(120), nullable=False)
    webhook_url = Column(String(255), nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )