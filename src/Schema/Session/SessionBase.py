from pydantic import BaseModel


class SessionBase(BaseModel):
    session_id: str
