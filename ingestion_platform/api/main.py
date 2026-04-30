# ingestion_platform/api/main.py
from fastapi import FastAPI, HTTPException
from ingestion_platform.orchestrator.orchestrator import main as run_orchestrator
from ingestion_platform.serving.reader import get_latest_data
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

@app.get("/data/{source_name}")
def get_data(source_name: str, page: int = 1, limit: int = 50):
    print(f"page={page}, limit={limit}")
    try:
        return get_latest_data(source_name, page=page, limit=limit)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))