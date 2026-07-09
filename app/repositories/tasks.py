from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Task, User
from app import schemas

def create(task: schemas.TaskCreate, user: User, db:Session) -> Task:
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id = user.id,
        created_at = datetime.now(timezone.utc)
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update(task_update: schemas.TaskUpdate, db_task: Task, db:Session) -> Task:
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_user_tasks(user: User) -> list[Task]:
    return user.tasks

def delete(db_task: Task, db:Session) -> None:
    db.delete(db_task)
    db.commit()

def get(task_id: int, db: Session) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()
