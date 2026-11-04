from pydantic import BaseModel, Field, model_validator
from typing import Optional


class MarkCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=30)
    exam: str = Field(min_length=1, max_length=20)
    marks_obtained: Optional[float] = Field(default=None, ge=0)
    max_marks: float = Field(default=100, gt=0)
    is_absent: bool = False

    @model_validator(mode="after")
    def validate_marks(self):
        if (
            self.marks_obtained is not None
            and self.marks_obtained > self.max_marks
        ):
            raise ValueError("marks_obtained cannot exceed max_marks")

        return self


class MarkUpdate(BaseModel):
    subject: Optional[str] = Field(default=None, min_length=1, max_length=30)
    exam: Optional[str] = Field(default=None, min_length=1, max_length=20)
    marks_obtained: Optional[float] = Field(default=None, ge=0)
    max_marks: Optional[float] = Field(default=None, gt=0)
    is_absent: Optional[bool] = None

    @model_validator(mode="after")
    def validate_marks(self):
        if (
            self.marks_obtained is not None
            and self.max_marks is not None
            and self.marks_obtained > self.max_marks
        ):
            raise ValueError("marks_obtained cannot exceed max_marks")

        return self