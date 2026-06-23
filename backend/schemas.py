from __future__ import annotations

from datetime import date as Date
from datetime import datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["low", "medium", "high"]
HabitFrequency = Literal["daily", "weekdays"]
TaskStatus = Literal["active", "completed", "all"]


class CategoryBase(BaseModel):
    name: str
    color: str


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TaskBase(BaseModel):
    title: str
    notes: str | None = None
    date: Date
    start_time: time | None = None
    end_time: time | None = None
    priority: Priority = "medium"
    category_id: int | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    notes: str | None = None
    date: Date | None = None
    start_time: time | None = None
    end_time: time | None = None
    priority: Priority | None = None
    category_id: int | None = None
    is_completed: bool | None = None


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    color: str


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_completed: bool
    completed_at: datetime | None
    created_at: datetime
    category: CategoryBrief | None = None


class HabitBase(BaseModel):
    title: str
    icon: str
    frequency: HabitFrequency = "daily"
    reminder_time: time | None = None


class HabitCreate(HabitBase):
    pass


class HabitOut(HabitBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    streak: int = 0
    completed_today: bool = False


class HabitLogRequest(BaseModel):
    date: Date
    completed: bool = True


class DeviceRegister(BaseModel):
    id: str = Field(..., min_length=36, max_length=36)


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class WeeklyStat(BaseModel):
    day: str
    completion_rate: float
    total: int
    completed: int


class CategoryStat(BaseModel):
    category_id: int | None
    name: str
    color: str
    count: int


class StatsSummary(BaseModel):
    completed_this_week: int
    longest_streak: int
    points: int


class HabitStreakOut(BaseModel):
    habit_id: int
    title: str
    streak: int
