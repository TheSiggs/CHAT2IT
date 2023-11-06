import os
from datetime import datetime
from jose import jwt
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.Entity.AuthToken import AuthToken
from src.Repository import UserRepository

load_dotenv()


def get_auth_token(db: Session, auth_token: str):
    return db.query(AuthToken).filter(AuthToken.value == auth_token).first()


def get_auth_token_by_user(db: Session, user_id: int):
    return db.query(AuthToken).filter(AuthToken.user_id == user_id).all()


def get_auth_tokens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AuthToken).offset(skip).limit(limit).all()


def create_auth_token(db: Session, user_id: int):
    user = UserRepository.get_user(db=db, user_id=user_id)
    if user:
        db_item = AuthToken(user_id=user_id, value=create_access_token())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    else:
        return None


def create_access_token():
    to_encode = {
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'))
    return encoded_jwt
