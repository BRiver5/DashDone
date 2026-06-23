from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_device_id
from models import Category, Device, Task
from schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.device_id == device_id).order_by(Category.name).all()


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    device = db.get(Device, device_id)
    if not device:
        device = Device(id=device_id)
        db.add(device)
        db.flush()
    cat = Category(device_id=device_id, name=payload.name, color=payload.color)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id, Category.device_id == device_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.query(Task).filter(Task.category_id == category_id).update({Task.category_id: None})
    db.delete(cat)
    db.commit()
