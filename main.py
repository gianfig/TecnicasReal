from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

# Crear la aplicación FastAPI
app = FastAPI(
    title="API de Tareas",
    description="Una API simple para gestionar tareas",
    version="1.0.0"
)

# Modelo de datos para las tareas
class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[str] = None

# Base de datos en memoria (para simplicidad)
tasks_db = []

# Endpoints de la API

@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {"message": "¡Bienvenido a la API de Tareas!", "version": "1.0.0"}

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    """Obtener todas las tareas"""
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Obtener una tarea específica por ID"""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    """Crear una nueva tarea"""
    task_dict = task.dict()
    task_dict["id"] = str(uuid.uuid4())
    task_dict["created_at"] = datetime.now().isoformat()
    tasks_db.append(task_dict)
    return task_dict

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task: Task):
    """Actualizar una tarea existente"""
    for i, existing_task in enumerate(tasks_db):
        if existing_task["id"] == task_id:
            task_dict = task.dict()
            task_dict["id"] = task_id
            task_dict["created_at"] = existing_task["created_at"]  # Mantener fecha de creación
            tasks_db[i] = task_dict
            return task_dict
    raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Eliminar una tarea"""
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            deleted_task = tasks_db.pop(i)
            return {"message": "Tarea eliminada", "task": deleted_task}
    raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.get("/tasks/completed", response_model=List[Task])
async def get_completed_tasks():
    """Obtener solo las tareas completadas"""
    return [task for task in tasks_db if task["completed"]]

@app.get("/tasks/pending", response_model=List[Task])
async def get_pending_tasks():
    """Obtener solo las tareas pendientes"""
    return [task for task in tasks_db if not task["completed"]]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
