from src.Schema.AuthToken.AuthTokenBase import AuthTokenBase


class AuthToken(AuthTokenBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
