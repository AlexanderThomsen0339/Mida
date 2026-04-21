from fastapi import APIRouter
from API.controllers.source_controller import get_all_sources, get_single_source

router = APIRouter()

@router.get("/")
def list_sources():
    return get_all_sources()

@router.get("/{source_id}")
def get_source(source_id: int):
    return get_single_source(source_id)