from fastapi import APIRouter, Depends
from API.controllers.source_controller import get_all_sources, get_single_source
from API.core.security import get_current_user

router = APIRouter()

@router.get("/")
def list_sources(current_user = Depends(get_current_user)):
    return get_all_sources()

@router.get("/{source_id}")
def get_source(source_id: int, current_user = Depends(get_current_user)):
    return get_single_source(source_id)