"""User profile schemas implementation."""

from pydantic import BaseModel
from typing import Optional


class UserProfileInput(BaseModel):
    username: str

    class Config:
        """Enable object relational mapping"""
        orm_mode = True


class UserProfileCategoryInput(BaseModel):
    username: str
    category: str

    class Config:
        """Enable object relational mapping"""
        orm_mode = True


class UserAddressInput(BaseModel):
    username: str
    address: Optional[str]

    class Config:
        """Enable object relational mapping"""
        orm_mode = True
