from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import bearer
from app import schemas
from app.dependencies import get_db
from app.services import tasks
from app.models import User

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model=schemas.TaskRead)
def create_task(
    task: schemas.TaskCreate,
    user = Depends(bearer.get_current_user),
    db: Session = Depends(get_db)
):
    return tasks.create_task(task, user, db)

@router.get("/{task_id}", response_model=schemas.TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(bearer.get_current_user)
):
    return tasks.get_task_for_user(task_id, user, db)

@router.get("/", response_model=list[schemas.TaskRead])
def get_tasks(user: User = Depends(bearer.get_current_user)):
    return tasks.get_tasks_for_user(user)

@router.patch("/{task_id}", response_model=schemas.TaskRead)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(bearer.get_current_user)
):
    return tasks.update_task_for_user(task_id, task, user, db)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(bearer.get_current_user)
):
    tasks.delete_task_for_user(task_id, user, db)
    return {"message": "Task deleted"}