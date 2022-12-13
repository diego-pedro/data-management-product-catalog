"""Authentication schemas implementation."""

from pydantic import BaseModel


class Authentication(BaseModel):
    username: str
    password: str

    class Config:
        """Enable object relational mapping"""
        orm_mode = True