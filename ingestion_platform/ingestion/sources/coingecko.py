import requests
import pandas as pd
from base_ingestion import BaseIngestion

class CoinGeckoIngestor(BaseIngestion):

    def __init__(self, source_id: int, source_name: str, config: dict):
        super().__init__(source_id, source_name, config)

    def fetch_data(self) -> pd.DataFrame:
        self._log("Henter data fra CoinGecko API...")
        response = requests.get(self.config["api_url"])
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)

    def save_raw_data(self, df: pd.DataFrame) -> None:
        path = f"lake/{self.source_name}/{pd.Timestamp.now().strftime('%Y/%m/%d/%H/%M')}/data.parquet"
        self._write_to_parquet(df, path)
        self._log(f"Data gemt: {path}")

    def run(self) -> None:
        self.db_manager.start()
        try:
            df = self.fetch_data()
            self.save_raw_data(df)
            self.db_manager.success("Ingestion fuldført.")
        except Exception as e:
            self.db_manager.fail(str(e))
            raise