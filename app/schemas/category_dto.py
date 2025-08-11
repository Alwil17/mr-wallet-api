from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CategoryCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    color: Optional[str] = Field(
        None, max_length=20, description="Optional color hex code"
    )
    icon: Optional[str] = Field(None, max_length=50, description="Optional icon name")


class CategoryUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: Optional[str] = None
    icon: Optional[str] = None
    user_id: int

    model_config = ConfigDict(from_attributes=True)
