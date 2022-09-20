from pydantic import BaseModel
from typing import List

class Rushee(BaseModel):
    name: str
    rank: int
    app_score: float
    gi_score: float
    ii_score: str
    bhs_score: int
    total_score: float
    strike: int