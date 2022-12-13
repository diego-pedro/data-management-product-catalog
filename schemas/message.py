from typing import Optional

from pydantic import BaseModel


class MessageInput(BaseModel):
    service: str
    username: str
    detail: str
    test_indicator: Optional[bool] = False

    class Config:
        """Enable object relational mapping"""
        orm_mode = True
