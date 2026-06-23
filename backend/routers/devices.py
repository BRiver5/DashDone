from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_device_id
from models import Device
from schemas import DeviceOut, DeviceRegister

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=DeviceOut)
def register_device(payload: DeviceRegister, db: Session = Depends(get_db)):
    device = db.get(Device, payload.id)
    if not device:
        device = Device(id=payload.id, created_at=datetime.utcnow())
        db.add(device)
        db.commit()
        db.refresh(device)
    return device


@router.delete("/{device_id}/data", status_code=204)
def clear_device_data(device_id: str, db: Session = Depends(get_db), header_id: str = Depends(get_device_id)):
    if device_id != header_id:
        raise HTTPException(status_code=403, detail="Device ID mismatch")
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
