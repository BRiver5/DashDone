from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_device_id
from models import Habit
from schemas import CategoryStat, HabitStreakOut, StatsSummary, WeeklyStat
from services.stats import get_category_stats, get_summary, get_weekly_stats
from services.streak import compute_streak

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/weekly", response_model=list[WeeklyStat])
def weekly_stats(device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    return get_weekly_stats(db, device_id)


@router.get("/categories", response_model=list[CategoryStat])
def category_stats(device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    return get_category_stats(db, device_id)


@router.get("/summary", response_model=StatsSummary)
def summary_stats(device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    return get_summary(db, device_id)


@router.get("/habit-streaks", response_model=list[HabitStreakOut])
def habit_streaks(device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    habits = db.query(Habit).filter(Habit.device_id == device_id).all()
    return [
        HabitStreakOut(habit_id=h.id, title=h.title, streak=compute_streak(db, h))
        for h in habits
    ]
