from src.Schema.AuthToken.AuthToken import AuthToken
from src.Schema.Session.Session import Session
from src.Schema.User.UserBase import UserBase


class User(UserBase):
    sessions: list[Session] = []
    auth_tokens: list[AuthToken] = []

    class Config:
        orm_mode = True
