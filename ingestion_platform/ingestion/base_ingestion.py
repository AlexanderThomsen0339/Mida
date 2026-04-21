"""
base_ingestion.py
------------------
En abstrakt base-klasse for ingestion, som kildespecifikke ingest.py-scripts kan arve fra.
"""
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from shared.db_manager import Configuration_manager

class BaseIngestion(ABC):
    db_manager: Configuration_manager
    LAKE_ROOT = Path(__file__).resolve().parent.parent / "lake"

    def __init__(self, source_id: int, source_name: str, config: dict) -> None:
        self.source_id = source_id
        self.source_name = source_name
        self.config = config
        self.db_manager = Configuration_manager(source_id)
        super().__init__()

    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_raw_data(self, df: pd.DataFrame) -> None:
        pass

    def _write_to_parquet(self, df: pd.DataFrame, path: str) -> None:
        full_path = self.LAKE_ROOT / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(full_path, index=False)

    def _log(self, message: str, log_type: str = "INFO") -> None:
        self.db_manager.log(message, log_type)