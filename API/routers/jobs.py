from fastapi import APIRouter, Depends
from API.controllers.jobs_controller import get_all_jobs, get_logs_for_job
from API.core.security import get_current_user

router = APIRouter()

@router.get("/")
def list_jobs(current_user = Depends(get_current_user)):
    return get_all_jobs()

@router.get("/{job_id}/logs")
def get_job_logs(job_id: int, current_user = Depends(get_current_user)):
    return get_logs_for_job(job_id)