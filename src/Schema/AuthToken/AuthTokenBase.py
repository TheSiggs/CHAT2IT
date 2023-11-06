from pydantic import BaseModel


class AuthTokenBase(BaseModel):
    value: str
