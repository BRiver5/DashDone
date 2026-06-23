import enum
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class HabitFrequency(str, enum.Enum):
    daily = "daily"
    weekdays = "weekdays"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    categories: Mapped[list["Category"]] = relationship(back_populates="device", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="device", cascade="all, delete-orphan")
    habits: Mapped[list["Habit"]] = relationship(back_populates="device", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(7))

    device: Mapped["Device"] = relationship(back_populates="categories")
    tasks: Mapped[list["Task"]] = relationship(back_populates="category")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.medium)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    device: Mapped["Device"] = relationship(back_populates="tasks")
    category: Mapped["Category | None"] = relationship(back_populates="tasks")


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    icon: Mapped[str] = mapped_column(String(50))
    frequency: Mapped[HabitFrequency] = mapped_column(Enum(HabitFrequency), default=HabitFrequency.daily)
    reminder_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    device: Mapped["Device"] = relationship(back_populates="habits")
    logs: Mapped[list["HabitLog"]] = relationship(back_populates="habit", cascade="all, delete-orphan")


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=True)

    habit: Mapped["Habit"] = relationship(back_populates="logs")
