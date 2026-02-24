from pydantic import BaseModel, Field
from typing import List


class CompanyAnalysis(BaseModel):
    company: str = Field(...)
    summary: str = Field(...)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)