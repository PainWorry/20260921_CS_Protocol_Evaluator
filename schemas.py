from pydantic import BaseModel, Field
from typing import List

class EvaluationCriterion(BaseModel):
    criterion: str = Field(..., description="The specific protocol rule being evaluated.")
    passed: bool = Field(..., description="True if the employee followed the protocol, False otherwise.")
    evidence: str = Field(..., description="Direct quote from the transcript as evidence.")
    reasoning: str = Field(..., description="Brief reasoning for why it passed or failed.")

class EvaluationReport(BaseModel):
    overall_score: float = Field(..., description="Overall compliance score from 0 to 100.", ge=0, le=100)
    checklist: List[EvaluationCriterion] = Field(..., description="List of evaluated criteria.")

class EvaluateRequest(BaseModel):
    transcript: str = Field(..., description="The chat or voice transcript to evaluate.")
    sop: str = Field(..., description="The Standard Operating Procedure text.")
