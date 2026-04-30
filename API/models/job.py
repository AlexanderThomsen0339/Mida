from pydantic import BaseModel
from datetime import datetime

class Job(BaseModel):
    JobID: int
    SourceID: int
    Timestamp: datetime
    Status: str

class JobLog(BaseModel):
    RunID: int
    JobID: int
    Timestamp: datetime
    Type: str
    Message: str