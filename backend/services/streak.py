from datetime import date, timedelta

from sqlalchemy.orm import Session

from models import Habit, HabitFrequency, HabitLog


def is_valid_habit_day(d: date, frequency: HabitFrequency) -> bool:
    if frequency == HabitFrequency.daily:
        return True
    return d.weekday() < 5


def compute_streak(db: Session, habit: Habit, from_date: date | None = None) -> int:
    current = from_date or date.today()
    streak = 0

    while True:
        if not is_valid_habit_day(current, habit.frequency):
            current -= timedelta(days=1)
            continue

        log = (
            db.query(HabitLog)
            .filter(HabitLog.habit_id == habit.id, HabitLog.date == current, HabitLog.completed.is_(True))
            .first()
        )
        if not log:
            break
        streak += 1
        current -= timedelta(days=1)

    return streak


def is_completed_on(db: Session, habit_id: int, on_date: date) -> bool:
    log = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id, HabitLog.date == on_date, HabitLog.completed.is_(True))
        .first()
    )
    return log is not None
