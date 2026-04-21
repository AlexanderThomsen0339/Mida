from fastapi import APIRouter
from API.controllers.jobs_controller import get_all_jobs, get_logs_for_job

router = APIRouter()

@router.get("/")
def list_jobs():
    return get_all_jobs()

@router.get("/{job_id}/logs")
def get_job_logs(job_id: int):
    return get_logs_for_job(job_id)