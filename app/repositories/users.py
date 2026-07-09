from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import User
from app import schemas
from app.security import hash_password

def create_user(user: schemas.UserCreate, db: Session) -> User:
    db_user = User(
        username = user.username,
        password = hash_password(user.password),
        created_at = datetime.now(timezone.utc)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session) -> list[User]:
    return db.query(User).all()

def get_user_by_id(id: int, db: Session) -> User | None:
    return db.query(User).filter(User.id == id).first()

def get_user_by_username(username: str, db: Session) -> User | None:
    return db.query(User).filter(User.username == username).first()