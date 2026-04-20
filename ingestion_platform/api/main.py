# ingestion_platform/api/main.py
from fastapi import FastAPI
from ingestion_platform.orchestrator.orchestrator import main as run_orchestrator
import threading

app = FastAPI()

@app.post("/trigger/all")
def trigger_all():
    threading.Thread(target=run_orchestrator).start()
    return {"status": "started"}

@app.post("/trigger/{source_id}")
def trigger_one(source_id: int):
    threading.Thread(target=run_orchestrator, kwargs={"source_id": source_id}).start()
    return {"status": "started", "source_id": source_id}