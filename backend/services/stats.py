from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Category, Habit, Task
from schemas import CategoryStat, StatsSummary, WeeklyStat
from services.streak import compute_streak


DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def get_weekly_stats(db: Session, device_id: str) -> list[WeeklyStat]:
    start = week_start(date.today())
    results: list[WeeklyStat] = []

    for i in range(7):
        day = start + timedelta(days=i)
        total = db.query(Task).filter(Task.device_id == device_id, Task.date == day).count()
        completed = (
            db.query(Task)
            .filter(Task.device_id == device_id, Task.date == day, Task.is_completed.is_(True))
            .count()
        )
        rate = (completed / total) if total > 0 else 0.0
        results.append(
            WeeklyStat(
                day=DAY_NAMES[i],
                completion_rate=round(rate, 2),
                total=total,
                completed=completed,
            )
        )
    return results


def get_category_stats(db: Session, device_id: str) -> list[CategoryStat]:
    start = week_start(date.today())
    end = start + timedelta(days=6)

    rows = (
        db.query(Category.id, Category.name, Category.color, func.count(Task.id))
        .outerjoin(Task, (Task.category_id == Category.id) & (Task.device_id == device_id))
        .filter(
            Category.device_id == device_id,
            (Task.date.is_(None)) | ((Task.date >= start) & (Task.date <= end)),
        )
        .group_by(Category.id)
        .all()
    )

    uncategorized = (
        db.query(func.count(Task.id))
        .filter(
            Task.device_id == device_id,
            Task.category_id.is_(None),
            Task.date >= start,
            Task.date <= end,
        )
        .scalar()
        or 0
    )

    stats = [
        CategoryStat(category_id=r[0], name=r[1], color=r[2], count=r[3])
        for r in rows
        if r[3] > 0
    ]
    if uncategorized > 0:
        stats.append(CategoryStat(category_id=None, name="Uncategorized", color="#6B7280", count=uncategorized))
    return stats


def get_summary(db: Session, device_id: str) -> StatsSummary:
    start = week_start(date.today())
    end = start + timedelta(days=6)

    completed_this_week = (
        db.query(Task)
        .filter(
            Task.device_id == device_id,
            Task.date >= start,
            Task.date <= end,
            Task.is_completed.is_(True),
        )
        .count()
    )

    habits = db.query(Habit).filter(Habit.device_id == device_id).all()
    longest_streak = max((compute_streak(db, h) for h in habits), default=0)
    points = completed_this_week * 10 + longest_streak * 5

    return StatsSummary(
        completed_this_week=completed_this_week,
        longest_streak=longest_streak,
        points=points,
    )
