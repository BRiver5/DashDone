from datetime import date as Date
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_device_id
from models import Device, Habit, HabitLog
from schemas import HabitCreate, HabitLogRequest, HabitOut, HabitStreakOut
from services.streak import compute_streak, is_completed_on

router = APIRouter(prefix="/habits", tags=["habits"])


def _habit_out(db: Session, habit: Habit, for_date: Date | None = None) -> HabitOut:
    view_date = for_date or Date.today()
    return HabitOut(
        id=habit.id,
        title=habit.title,
        icon=habit.icon,
        frequency=habit.frequency.value,
        reminder_time=habit.reminder_time,
        created_at=habit.created_at,
        streak=compute_streak(db, habit),
        completed_today=is_completed_on(db, habit.id, view_date),
    )


@router.get("", response_model=list[HabitOut])
def list_habits(
    for_date: Date | None = Query(None, alias="for_date"),
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    habits = db.query(Habit).filter(Habit.device_id == device_id).order_by(Habit.created_at).all()
    return [_habit_out(db, h, for_date) for h in habits]


@router.post("", response_model=HabitOut, status_code=201)
def create_habit(payload: HabitCreate, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    device = db.get(Device, device_id)
    if not device:
        device = Device(id=device_id)
        db.add(device)
        db.flush()
    habit = Habit(device_id=device_id, **payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return _habit_out(db, habit)


@router.delete("/{habit_id}", status_code=204)
def delete_habit(habit_id: int, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.device_id == device_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()


@router.post("/{habit_id}/log", response_model=HabitOut)
def log_habit(
    habit_id: int,
    payload: HabitLogRequest,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.device_id == device_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log = db.query(HabitLog).filter(HabitLog.habit_id == habit_id, HabitLog.date == payload.date).first()
    if payload.completed:
        if not log:
            log = HabitLog(habit_id=habit_id, date=payload.date, completed=True)
            db.add(log)
        else:
            log.completed = True
    elif log:
        db.delete(log)
    db.commit()
    return _habit_out(db, habit, payload.date)


@router.get("/{habit_id}/streak", response_model=HabitStreakOut)
def get_streak(habit_id: int, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.device_id == device_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return HabitStreakOut(habit_id=habit.id, title=habit.title, streak=compute_streak(db, habit))
