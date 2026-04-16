import requests
import pandas as pd
from datetime import datetime

import base_ingestion as bi

class restcountries(bi.BaseIngestion):
    def __init__(self):
        super().__init__()

    def fetch_data(self) -> pd.DataFrame:
        response = requests.get(self.config["api_url"])
        data = response.json()
        df = pd.DataFrame(data)
        return df
    
    def save_raw_data(self, df: pd.DataFrame) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"lake/coingecko/raw/coingecko_{ts}.parquet"
        self._write_to_parquet(df, out_path)
        
