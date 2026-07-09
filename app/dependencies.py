from typing import Generator
from app.database import session_local
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    db = session_local()
    try:
        yield db
    finally:
        db.close()