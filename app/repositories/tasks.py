from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Task, User
from app import schemas

async def create(task: schemas.TaskCreate, user: User, db:AsyncSession) -> Task:
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id = user.id,
        created_at = datetime.now(timezone.utc)
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def update(task_update: schemas.TaskUpdate, db_task: Task, db:AsyncSession) -> Task:
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def get_user_tasks(user: User, db:AsyncSession) -> list[Task]:
    result = await db.execute(select(Task).where(Task.user_id == user.id))
    return list(result.scalars().all())

async def delete(db_task: Task, db:AsyncSession) -> None:
    await db.delete(db_task)
    await db.commit()

async def get(task_id: int, db: AsyncSession) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()
