from shared.db_manager import get_jobs, get_job_logs

def get_all_jobs():
    return get_jobs()

def get_logs_for_job(job_id: int):
    return get_job_logs(job_id)