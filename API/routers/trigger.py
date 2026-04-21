from fastapi import APIRouter
from API.controllers.trigger_controller import trigger_all, trigger_source

router = APIRouter()

@router.post("/all")
def run_all():
    return trigger_all()

@router.post("/{source_id}")
def run_source(source_id: int):
    return trigger_source(source_id)