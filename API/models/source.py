from pydantic import BaseModel
from datetime import datetime

class Source(BaseModel):
    SourceID: int
    SourceName: str
    Source_URL: str
    Authentication: str | None
    UPDATED_AT: datetime