import json
import pandas as pd
from pathlib import Path

LAKE_ROOT  = Path(__file__).resolve().parent.parent / "lake"
CACHE_PATH = Path(__file__).resolve().parent / "cache.json"


def get_latest_data(source_name: str, use_cache: bool = True, page: int = 1, limit: int = 50) -> dict:
    # Find seneste parquet fil
    source_path = LAKE_ROOT / source_name
    parquet_files = sorted(source_path.rglob("data.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"Ingen parquet filer fundet for kilde '{source_name}'")

    df = pd.read_parquet(parquet_files[-1])
    
    total = len(df)
    start = (page - 1) * limit
    end   = start + limit
    page_df = df.iloc[start:end]
    
    # Paginer INDEN konvertering til dict
    page_df = page_df.where(pd.notnull(page_df), None)

    return {
        "source":      source_name,
        "total":       total,
        "page":        page,
        "limit":       limit,
        "total_pages": -(-total // limit),
        "data":        page_df.to_dict(orient="records")
    }