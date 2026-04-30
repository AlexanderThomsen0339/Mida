from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from API.routers import sources, jobs, trigger, auth, data

app = FastAPI(title="MIDA API", version="1.0.0")

app.include_router(auth.router,    prefix="/auth",    tags=["Auth"])
app.include_router(sources.router, prefix="/sources", tags=["Sources"])
app.include_router(jobs.router,    prefix="/jobs",    tags=["Jobs"])
app.include_router(trigger.router, prefix="/trigger", tags=["Trigger"])
app.include_router(data.router, prefix="/data", tags=["Data"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)