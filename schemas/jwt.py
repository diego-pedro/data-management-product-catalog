"""JWT Schema Settings."""
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"

