# API/routers/data.py
from fastapi import APIRouter, Depends
from controllers.data_controller import get_source_data
from core.security import get_current_user

router = APIRouter()

@router.get("/{source_name}")
def get_data(source_name: str, page: int = 1, limit: int = 50, current_user = Depends(get_current_user)):
    return get_source_data(source_name, page=page, limit=limit)