import json
from pathlib import Path

CACHE_PATH = Path(__file__).resolve().parent / "cache.json"

def get_latest_data(source_name: str, page: int = 1, limit: int = 50) -> dict:
    if not CACHE_PATH.exists():
        raise FileNotFoundError("Cache findes ikke endnu")
    
    cache = json.loads(CACHE_PATH.read_text())
    
    if source_name not in cache:
        raise KeyError(f"Ingen data i cache for kilde '{source_name}'")
    
    records = cache[source_name]["data"]
    total   = len(records)
    start   = (page - 1) * limit
    end     = start + limit

    return {
        "source":      source_name,
        "total":       total,
        "page":        page,
        "limit":       limit,
        "total_pages": -(-total // limit),
        "data":        records[start:end]
    }