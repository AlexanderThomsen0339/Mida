from fastapi import APIRouter, Depends
from API.controllers.trigger_controller import trigger_all, trigger_source
from API.core.security import get_current_user

router = APIRouter()

@router.post("/all")
def run_all(current_user = Depends(get_current_user)):
    return trigger_all()

@router.post("/{source_id}")
def run_source(source_id: int, current_user = Depends(get_current_user)):
    return trigger_source(source_id)