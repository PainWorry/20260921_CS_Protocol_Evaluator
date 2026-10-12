import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types
from schemas import EvaluationReport

# The client automatically picks up GEMINI_API_KEY from the environment
client = genai.Client()

def evaluate_transcript(transcript: str, sop: str) -> EvaluationReport:
    """
    Evaluates a transcript against an SOP using Gemini, enforcing the Pydantic schema.
    """
    prompt = f"""
    You are an elite QA Evaluator for a Customer Service team.
    Evaluate the following transcript against the provided Standard Operating Procedure (SOP).
    
    SOP:
    {sop}
    
    Transcript:
    {transcript}
    
    Output the evaluation strictly adhering to the requested JSON schema. Provide direct quotes as evidence.
    """
    
    # Generate content enforcing the Pydantic schema structure
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EvaluationReport
        )
    )
    
    # Parse the validated JSON back into the Pydantic model
    return EvaluationReport.model_validate_json(response.text)
