from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Task, User
from app import schemas
from app.repositories import tasks as task_repo

def create_task(
    task_data: schemas.TaskCreate,
    user: User,
    db: Session,
) -> Task:
    return task_repo.create(task_data, user, db)

def get_task_for_user(
    task_id: int,
    user: User,
    db: Session,
) -> Task:
    task = task_repo.get(task_id, db)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

def get_tasks_for_user(user: User) -> list[Task]:
    return task_repo.get_user_tasks(user)

def update_task_for_user(
    task_id: int,
    task_data: schemas.TaskUpdate,
    user: User,
    db: Session,
) -> Task:
    task = get_task_for_user(task_id, user, db)
    return task_repo.update(task_data, task, db)

def delete_task_for_user(
    task_id: int,
    user: User,
    db: Session,
) -> None:
    task = get_task_for_user(task_id, user, db)
    task_repo.delete(task, db)