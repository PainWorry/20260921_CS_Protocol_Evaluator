from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from schemas import EvaluateRequest, EvaluationReport
from evaluator import evaluate_transcript

app = FastAPI(
    title="CS Protocol Evaluator API",
    description="API for evaluating CS transcripts against SOPs using structured LLM outputs.",
    version="0.1.0"
)

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

@app.post("/evaluate", response_model=EvaluationReport)
def evaluate_endpoint(request: EvaluateRequest):
    """
    Evaluates a transcript against the provided SOP and returns a structured JSON report.
    """
    try:
        report = evaluate_transcript(request.transcript, request.sop)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run the server locally:
# uvicorn main:app --reload
