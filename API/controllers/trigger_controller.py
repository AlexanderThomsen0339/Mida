import httpx

INGESTION_URL = "http://localhost:8001"

def trigger_all():
    response = httpx.post(f"{INGESTION_URL}/trigger/all")
    return response.json()

def trigger_source(source_id: int):
    response = httpx.post(f"{INGESTION_URL}/trigger/{source_id}")
    return response.json()