from fastapi import FastAPI
from app.routers import auth_router, task_router

app = FastAPI(
    title="TaskManager API Pet-project",
    version="1.0.0"
)

app.include_router(auth_router.router)
app.include_router(task_router.router)

@app.get("/")
def root():
    return {"message": "Task manager API is running"}
