from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Task, User
from app import schemas
from app.repositories import tasks as task_repo

async def create_task(
    task_data: schemas.TaskCreate,
    user: User,
    db: AsyncSession,
) -> Task:
    return await task_repo.create(task_data, user, db)

async def get_task_for_user(
    task_id: int,
    user: User,
    db: AsyncSession,
) -> Task:
    task = await task_repo.get(task_id, db)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

async def get_tasks_for_user(user: User, db:AsyncSession) -> list[Task]:
    return await task_repo.get_user_tasks(user, db)

async def update_task_for_user(
    task_id: int,
    task_data: schemas.TaskUpdate,
    user: User,
    db: AsyncSession,
) -> Task:
    task = await get_task_for_user(task_id, user, db)
    return await task_repo.update(task_data, task, db)

async def delete_task_for_user(
    task_id: int,
    user: User,
    db: AsyncSession,
) -> None:
    task = await get_task_for_user(task_id, user, db)
    await task_repo.delete(task, db)