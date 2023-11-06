from src.Schema.Session.SessionBase import SessionBase


class Session(SessionBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
