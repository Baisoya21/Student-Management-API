from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date
from typing import Optional


class StudentCreate(BaseModel):
    school_id: int = Field(gt=0)
    roll_no: int = Field(gt=0)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    father_name: Optional[str] = Field(default=None, max_length=100)
    class_name: str = Field(min_length=1, max_length=5, alias="class")
    section: str = Field(min_length=1, max_length=1)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None

    model_config = {"populate_by_name": True}

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value is not None and value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value


class StudentUpdate(BaseModel):
    school_id: int = Field(gt=0)
    roll_no: int = Field(gt=0)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    father_name: Optional[str] = Field(default=None, max_length=100)
    class_name: str = Field(min_length=1, max_length=5, alias="class")
    section: str = Field(min_length=1, max_length=1)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None

    model_config = {"populate_by_name": True}

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value is not None and value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value


class StudentPatch(BaseModel):
    school_id: Optional[int] = Field(default=None, gt=0)
    roll_no: Optional[int] = Field(default=None, gt=0)
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    father_name: Optional[str] = Field(default=None, max_length=100)
    class_name: Optional[str] = Field(default=None, min_length=1, max_length=5, alias="class")
    section: Optional[str] = Field(default=None, min_length=1, max_length=1)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None

    model_config = {"populate_by_name": True}

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value is not None and value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value