from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
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
async def create_task(
    task: schemas.TaskCreate,
    user = Depends(bearer.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await tasks.create_task(task, user, db)

@router.get("/{task_id}", response_model=schemas.TaskRead)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(bearer.get_current_user)
):
    return await tasks.get_task_for_user(task_id, user, db)

@router.get("/", response_model=list[schemas.TaskRead])
async def get_tasks(
    user: User = Depends(bearer.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await tasks.get_tasks_for_user(user, db)

@router.patch("/{task_id}", response_model=schemas.TaskRead)
async def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(bearer.get_current_user)
):
    return await tasks.update_task_for_user(task_id, task, user, db)

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(bearer.get_current_user)
):
    await tasks.delete_task_for_user(task_id, user, db)
    return {"message": "Task deleted"}