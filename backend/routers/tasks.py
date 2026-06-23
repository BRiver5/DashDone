from datetime import date as Date
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from dependencies import get_device_id
from models import Category, Device, Priority, Task
from schemas import CategoryCreate, CategoryOut, TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _ensure_device(db: Session, device_id: str):
    device = db.get(Device, device_id)
    if not device:
        device = Device(id=device_id)
        db.add(device)
        db.commit()


def _task_query(db: Session, device_id: str):
    return db.query(Task).options(joinedload(Task.category)).filter(Task.device_id == device_id)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    task_date: Date | None = Query(None, alias="date"),
    category: int | None = Query(None),
    priority: Priority | None = Query(None),
    status: str | None = Query(None),
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    q = _task_query(db, device_id)
    if task_date:
        q = q.filter(Task.date == task_date)
    if category is not None:
        q = q.filter(Task.category_id == category)
    if priority:
        q = q.filter(Task.priority == priority)
    if status == "active":
        q = q.filter(Task.is_completed.is_(False))
    elif status == "completed":
        q = q.filter(Task.is_completed.is_(True))
    return q.order_by(Task.date, Task.start_time).all()


@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    _ensure_device(db, device_id)
    if payload.category_id:
        cat = db.query(Category).filter(Category.id == payload.category_id, Category.device_id == device_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
    task = Task(device_id=device_id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_query(db, device_id).filter(Task.id == task.id).first()


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    task = _task_query(db, device_id).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    task = _task_query(db, device_id).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    data = payload.model_dump(exclude_unset=True)
    if "is_completed" in data:
        task.is_completed = data.pop("is_completed")
        task.completed_at = datetime.utcnow() if task.is_completed else None
    for k, v in data.items():
        setattr(task, k, v)
    db.commit()
    return _task_query(db, device_id).filter(Task.id == task_id).first()


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    task = _task_query(db, device_id).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
