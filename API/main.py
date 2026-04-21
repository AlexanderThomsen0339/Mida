# API/main.py
from fastapi import FastAPI
from API.routers import sources, jobs, trigger

app = FastAPI(title="MIDA API", version="1.0.0")

app.include_router(sources.router, prefix="/sources", tags=["Sources"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(trigger.router, prefix="/trigger", tags=["Trigger"])