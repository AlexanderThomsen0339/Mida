# API/controllers/data_controller.py
import httpx

INGESTION_URL = "http://localhost:8001"

def get_source_data(source_name: str, page: int = 1, limit: int = 50):
    response = httpx.get(f"{INGESTION_URL}/data/{source_name}", params={"page": page, "limit": limit})
    response.raise_for_status()
    return response.json()