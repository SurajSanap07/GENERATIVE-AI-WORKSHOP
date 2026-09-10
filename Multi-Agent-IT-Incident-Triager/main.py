import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI


app = FastAPI(
    title="Multi-Agent IT Incident Triager",
    description="AI-powered IT incident analysis using multiple agents",
    version="1.0.0"
)


# ==========================================
# OpenRouter Configuration
# ==========================================

MODEL_NAME = os.environ.get(
    "OPENROUTER_MODEL",
    "openrouter/free"
)


def get_client():

    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY not configured."
        )

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )


# ==========================================
# Request / Response Models
# ==========================================

class IncidentRequest(BaseModel):
    ticket_id: str
    raw_log: str


class IncidentResponse(BaseModel):
    ticket_id: str
    extracted_error: str
    severity: str
    recommended_action: str


# ==========================================
# Common AI Generation Function
# ==========================================

def generate_response(client, prompt: str) -> str:

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response.choices[0].message.content

        if not result:
            raise RuntimeError("Empty response from OpenRouter.")

        return result.strip()

    except Exception as e:

        print("OpenRouter API Error:", repr(e))

        raise HTTPException(
            status_code=502,
            detail=f"OpenRouter API request failed: {str(e)}"
        )


# ==========================================
# AGENT 1
# Error Extraction Agent
# ==========================================

def extractor_agent(client, raw_log: str) -> str:

    prompt = f"""
You are an IT Incident Error Extraction Agent.

Analyze the following system log.

Extract:
1. The root error message.
2. The affected service.

Return the result in exactly 2 short sentences.

System Log:
{raw_log}
"""

    return generate_response(client, prompt)


# ==========================================
# AGENT 2
# Severity Classification Agent
# ==========================================

def classifier_agent(client, error_summary: str) -> str:

    prompt = f"""
You are an IT Incident Severity Classification Agent.

Analyze the following error summary.

Assign exactly one severity level:

LOW
MEDIUM
HIGH
CRITICAL

Then explain the reason in one short sentence.

Error Summary:
{error_summary}
"""

    return generate_response(client, prompt)


# ==========================================
# AGENT 3
# Resolution Agent
# ==========================================

def resolution_agent(
    client,
    error_summary: str,
    severity: str
) -> str:

    prompt = f"""
You are an IT Incident Resolution Agent.

Create a concise 3-step action plan for resolving the incident.

Error:
{error_summary}

Severity:
{severity}

Return exactly 3 numbered steps.
"""

    return generate_response(client, prompt)


# ==========================================
# Health Check
# ==========================================

@app.get("/")
def health_check():

    return {
        "status": "Multi-Agent System Operational",
        "model": MODEL_NAME
    }


# ==========================================
# OpenRouter Test
# ==========================================

@app.get("/ai-test")
def ai_test():

    client = get_client()

    result = generate_response(
        client,
        "Reply with exactly: OpenRouter connection successful."
    )

    return {
        "status": "success",
        "response": result
    }


# ==========================================
# MULTI-AGENT ORCHESTRATOR
# ==========================================

@app.post("/triage", response_model=IncidentResponse)
async def triage_incident(request: IncidentRequest):

    client = get_client()

    # Agent 1
    extracted_error = extractor_agent(
        client,
        request.raw_log
    )

    # Agent 2
    severity_assessment = classifier_agent(
        client,
        extracted_error
    )

    # Agent 3
    action_plan = resolution_agent(
        client,
        extracted_error,
        severity_assessment
    )

    return IncidentResponse(
        ticket_id=request.ticket_id,
        extracted_error=extracted_error,
        severity=severity_assessment,
        recommended_action=action_plan
    )
