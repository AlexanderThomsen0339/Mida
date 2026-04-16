"""
base_ingestion.py
------------------

En abstrakt base-klasse for ingestion, som kildespecifikke ingest.py-scripts kan arve fra.
Idéen er, at vi kan flytte fælles funktionalitet og konventioner her, 
så kildespecifikke scripts kun skal fokusere på at hente data og gemme data råt i laken.
"""

from abc import ABC, abstractmethod
import pandas as pd
from db.db_manager import Configuration_manager

class BaseIngestion(ABC):

    db_manager: Configuration_manager
    def __init__(self, source_id: int, source_name: str, config: dict) -> None:
        self.source_id = source_id
        self.source_name = source_name
        self.config = config
        self.db_manager = Configuration_manager()
        super().__init__()

    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """
        Hent data fra API og returner som DataFrame.
        Skal implementeres af kildespecifikke ingest.py-scripts.
        """
        pass

    @abstractmethod
    def save_raw_data(self, df: pd.DataFrame) -> None:
        """
        Gem rå data i laken.
        Skal implementeres af kildespecifikke ingest.py-scripts.
        """
        pass

    def _write_to_parquet(self, df: pd.DataFrame, path: str) -> None:
        """
        Hjælpefunktion til at gemme DataFrame som Parquet.
        """
        df.to_parquet(path, index=False)
