from fastapi import Header, HTTPException


def get_device_id(x_device_id: str = Header(..., alias="X-Device-Id")) -> str:
    if not x_device_id or len(x_device_id) < 32:
        raise HTTPException(status_code=400, detail="Valid X-Device-Id header required")
    return x_device_id
